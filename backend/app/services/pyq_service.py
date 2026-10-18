"""PYQ Search Engine with hybrid BM25 and academic context filtering."""

import math
import re
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.academic import VerificationStatus
from app.models.question_paper import QuestionPaper, ExtractedQuestion
from app.models.academic import Subject, SyllabusUnit, SyllabusTopic
from app.schemas.question_paper import (
    PYQSearchQuery,
    PYQSearchResponse,
    PYQSearchResultItem,
    PYQMatchReason,
    ExtractedQuestionResponse,
)


def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text for BM25 search."""
    tokens = re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())
    # Filter very short tokens
    return [t for t in tokens if len(t) > 1]


class PYQSearchEngine:
    def __init__(self, db: Session):
        self.db = db

    def search(self, params: PYQSearchQuery) -> PYQSearchResponse:
        """
        Execute filtered and ranked PYQ search.
        Only verified questions from verified question papers are included.
        """
        # 1. Base query with joins
        query = (
            self.db.query(ExtractedQuestion, QuestionPaper, Subject, SyllabusUnit, SyllabusTopic)
            .join(QuestionPaper, ExtractedQuestion.paper_id == QuestionPaper.id)
            .join(Subject, QuestionPaper.subject_id == Subject.id)
            .outerjoin(SyllabusUnit, ExtractedQuestion.unit_id == SyllabusUnit.id)
            .outerjoin(SyllabusTopic, ExtractedQuestion.topic_id == SyllabusTopic.id)
            .filter(
                QuestionPaper.verification_status == VerificationStatus.VERIFIED,
                QuestionPaper.is_published == True,
                ExtractedQuestion.is_human_verified == True,
            )
        )

        # 2. Apply academic context filters
        if params.subject_id:
            query = query.filter(QuestionPaper.subject_id == params.subject_id)
        if params.scheme_id:
            query = query.filter(QuestionPaper.scheme_id == params.scheme_id)
        if params.branch_id:
            query = query.filter(Subject.branch_id == params.branch_id)
        if params.semester_number:
            query = query.filter(Subject.semester_number == params.semester_number)
        if params.unit_id:
            query = query.filter(ExtractedQuestion.unit_id == params.unit_id)
        if params.topic_id:
            query = query.filter(ExtractedQuestion.topic_id == params.topic_id)
        if params.exam_year:
            query = query.filter(QuestionPaper.exam_year == params.exam_year)
        if params.exam_session:
            query = query.filter(QuestionPaper.exam_session == params.exam_session)
        if params.marks:
            query = query.filter(ExtractedQuestion.marks == params.marks)

        records = query.all()
        if not records:
            return PYQSearchResponse(items=[], total=0, page=params.page, page_size=params.page_size, total_pages=0)

        # 3. If keyword query is provided, rank with BM25
        scored_items = []
        user_query_str = (params.query or "").strip()

        if user_query_str:
            query_tokens = tokenize(user_query_str)
            corpus = [tokenize(rec[0].question_text) for rec in records]

            if query_tokens and corpus:
                bm25 = BM25Okapi(corpus)
                bm25_scores = bm25.get_scores(query_tokens)
            else:
                bm25_scores = [0.0] * len(records)

            for i, (q, p, s, u, t) in enumerate(records):
                bm_score = float(bm25_scores[i])
                reasons = []

                if bm_score > 0.0:
                    reasons.append(
                        PYQMatchReason(
                            strategy="bm25_keyword",
                            score=round(bm_score, 3),
                            matched_term=user_query_str[:40],
                        )
                    )

                # Metadata match bonus
                meta_score = 0.0
                if params.unit_id and q.unit_id == params.unit_id:
                    meta_score += 1.0
                    reasons.append(PYQMatchReason(strategy="exact_unit", score=1.0))
                if params.topic_id and q.topic_id == params.topic_id:
                    meta_score += 1.5
                    reasons.append(PYQMatchReason(strategy="exact_topic", score=1.5))

                combined_score = bm_score + meta_score
                if bm_score > 0.0 or meta_score > 0.0:
                    scored_items.append((combined_score, q, p, s, u, t, reasons))

            # Sort by combined score descending
            scored_items.sort(key=lambda x: x[0], reverse=True)
        else:
            # No text query: sort by year desc, then question number
            for q, p, s, u, t in records:
                reasons = [PYQMatchReason(strategy="academic_filter", score=1.0)]
                scored_items.append((1.0, q, p, s, u, t, reasons))
            scored_items.sort(key=lambda x: (x[2].exam_year, -x[1].question_number), reverse=True)

        # 4. Pagination
        total = len(scored_items)
        start_idx = (params.page - 1) * params.page_size
        end_idx = start_idx + params.page_size
        page_slice = scored_items[start_idx:end_idx]

        items = []
        for score, q, p, s, u, t, reasons in page_slice:
            items.append(
                PYQSearchResultItem(
                    question=ExtractedQuestionResponse.model_validate(q),
                    paper_year=p.exam_year,
                    paper_session=p.exam_session,
                    paper_type=p.exam_type,
                    subject_code=s.code,
                    subject_name=s.name,
                    paper_source_url=p.source_url,
                    unit_title=u.title if u else None,
                    topic_name=t.topic_name if t else None,
                    match_reasons=reasons,
                    combined_score=round(score, 3),
                )
            )

        total_pages = math.ceil(total / params.page_size) if params.page_size > 0 else 1
        return PYQSearchResponse(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
        )
