"""AI Exam Tutor chat API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.academic import Subject
from app.models.chat import ChatSession, ChatMessage, Citation, RetrievalRecord
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatSessionResponse,
    ChatMessageResponse,
    CitationResponse,
)
from app.schemas.common import MessageResponse
from app.services.rag_service import RAGEngine

router = APIRouter(prefix="/chat", tags=["AI Exam Tutor"])


@router.post("/", response_model=ChatResponse)
def chat_with_tutor(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Interact with the RGPV AI Exam Tutor.
    - Classifies intent and strictly enforces academic scope.
    - Retrieves syllabus context and verified PYQs.
    - Formats answers by marks (2-mark, 7-mark, 14-mark) or conceptual derivations.
    - Returns traceable citations to syllabus units, paper year, and question numbers.
    """
    subject = db.query(Subject).filter(Subject.id == request.subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID {request.subject_id} not found."
        )

    # Resolve or create ChatSession
    if request.session_id:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == request.session_id, ChatSession.user_id == current_user.id)
            .first()
        )
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found.")
    else:
        session = ChatSession(
            user_id=current_user.id,
            subject_id=request.subject_id,
            title=f"{subject.code}: {request.message[:35]}...",
        )
        db.add(session)
        db.flush()

    # Save User message
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.message,
        is_within_scope=True,
    )
    db.add(user_msg)
    db.flush()

    # Execute RAG generation
    rag_engine = RAGEngine(db=db)
    result = rag_engine.generate_grounded_response(
        subject=subject,
        query=request.message,
        answer_format=request.answer_format or "explanation",
    )

    # Save Assistant message
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=result["reply"],
        intent_classification=result["intent"],
        is_within_scope=result["is_within_scope"],
    )
    db.add(assistant_msg)
    db.flush()

    # Save Citations
    citation_responses = []
    for cit in result["citations"]:
        citation_entry = Citation(
            message_id=assistant_msg.id,
            source_type=cit.source_type,
            source_id=cit.source_id,
            document_title=cit.document_title,
            university_name=cit.university_name,
            subject_code=cit.subject_code,
            unit_number=cit.unit_number,
            exam_year=cit.exam_year,
            exam_session=cit.exam_session,
            page_number=cit.page_number,
            question_number=cit.question_number,
            source_url=cit.source_url,
        )
        db.add(citation_entry)
        citation_responses.append(cit)

    # Log retrieval metrics
    retrieval_log = RetrievalRecord(
        message_id=assistant_msg.id,
        retrieval_type="hybrid_bm25_context",
        query_text=request.message,
        results_count=len(result["citations"]),
        latency_ms=result["latency_ms"],
    )
    db.add(retrieval_log)
    db.commit()

    return ChatResponse(
        session_id=session.id,
        message_id=assistant_msg.id,
        reply=result["reply"],
        is_within_scope=result["is_within_scope"],
        intent=result["intent"],
        citations=citation_responses,
        related_pyqs=result["related_pyqs"],
        latency_ms=result["latency_ms"],
    )


@router.get("/sessions", response_model=List[ChatSessionResponse])
def get_user_chat_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve chat history sessions for the current student."""
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full messages and citations for a chat session."""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return session


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a chat session."""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    db.delete(session)
    db.commit()
    return MessageResponse(message="Chat session deleted successfully.")
