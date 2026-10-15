"""Tests for RAG AI Tutor, scope restriction, formatting, and citations."""

def test_ai_tutor_in_scope_query(client, student_headers):
    payload = {
        "subject_id": 1,
        "message": "Explain Stack ADT and infix to postfix conversion with algorithm",
        "answer_format": "7_mark"
    }
    res = client.post("/api/v1/chat/", json=payload, headers=student_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_within_scope"] is True
    assert "Stack" in data["reply"]
    assert len(data["citations"]) >= 1
    # Check citation attributes
    cit = data["citations"][0]
    assert "RGPV" in cit["university_name"]
    assert cit["document_title"] is not None


def test_ai_tutor_out_of_scope_query(client, student_headers):
    payload = {
        "subject_id": 1,
        "message": "What is the latest movie review of the new cricket film?",
        "answer_format": "explanation"
    }
    res = client.post("/api/v1/chat/", json=payload, headers=student_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_within_scope"] is False
    assert data["intent"] == "out_of_scope"
    assert "Scope Notice" in data["reply"]


def test_chat_session_history(client, student_headers):
    # Fetch user chat sessions
    res = client.get("/api/v1/chat/sessions", headers=student_headers)
    assert res.status_code == 200
    sessions = res.json()
    assert len(sessions) >= 1
    session_id = sessions[0]["id"]

    # Fetch messages in that session
    detail_res = client.get(f"/api/v1/chat/sessions/{session_id}", headers=student_headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert len(detail["messages"]) >= 2  # user + assistant
