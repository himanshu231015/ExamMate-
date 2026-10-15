"""Tests for study planner, student feedback, and error reporting."""

from datetime import date, timedelta

def test_create_study_plan_and_complete_item(client, student_headers):
    exam_date = (date.today() + timedelta(days=30)).isoformat()
    plan_payload = {
        "subject_id": 1,
        "title": "Data Structures End-Sem Sprint",
        "target_exam_date": exam_date,
        "daily_hours": 3.0,
        "confidence_level": "medium"
    }

    res = client.post("/api/v1/study-plans/", json=plan_payload, headers=student_headers)
    assert res.status_code == 201
    plan_data = res.json()
    assert plan_data["title"] == "Data Structures End-Sem Sprint"
    assert len(plan_data["items"]) >= 1

    item_id = plan_data["items"][0]["id"]
    plan_id = plan_data["id"]

    # Toggle item completion
    patch_res = client.patch(
        f"/api/v1/study-plans/{plan_id}/items/{item_id}",
        json={"is_completed": True},
        headers=student_headers
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["is_completed"] is True


def test_submit_feedback_and_report(client, student_headers, reviewer_headers):
    # 1. Submit Feedback
    fb_payload = {
        "message_id": 2,  # Assistant message created in seed/chat test
        "rating": "helpful",
        "comment": "Accurate 7-mark explanation with algorithm steps."
    }
    fb_res = client.post("/api/v1/feedback/", json=fb_payload, headers=student_headers)
    assert fb_res.status_code == 201

    # 2. Submit Error Report
    report_payload = {
        "report_category": "broken_link",
        "target_type": "question_paper",
        "target_id": 1,
        "description": "Paper link was temporarily timing out on mobile browser."
    }
    rep_res = client.post("/api/v1/feedback/reports", json=report_payload, headers=student_headers)
    assert rep_res.status_code == 201
    report_id = rep_res.json()["id"]

    # 3. Reviewer/Admin views reports
    view_res = client.get("/api/v1/feedback/reports", headers=reviewer_headers)
    assert view_res.status_code == 200
    reports = view_res.json()
    assert any(r["id"] == report_id for r in reports)
