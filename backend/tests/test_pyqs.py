"""Tests for PYQ search engine, BM25 ranking, and question paper retrieval."""

def test_pyq_search_by_keyword(client):
    # Search for "AVL tree"
    res = client.get("/api/v1/pyqs/search?query=AVL tree")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    first_item = data["items"][0]
    assert "AVL" in first_item["question"]["question_text"]
    assert len(first_item["match_reasons"]) >= 1
    assert any(r["strategy"] == "bm25_keyword" for r in first_item["match_reasons"])
    assert first_item["paper_source_url"] is not None


def test_pyq_search_by_marks_and_semester(client):
    # Search 14-mark questions
    res = client.get("/api/v1/pyqs/search?marks=14")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["question"]["marks"] == 14


def test_get_paper_details_and_source_url(client):
    res = client.get("/api/v1/pyqs/papers/1")
    assert res.status_code == 200
    paper = res.json()
    assert paper["id"] == 1
    assert paper["exam_year"] == 2023
    assert len(paper["questions"]) >= 1
    assert paper["source_url"] is not None
