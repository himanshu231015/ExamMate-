"""Comprehensive tests for Admin Dashboard, Governance, RBAC, and Security."""

import pytest
from app.models.user import User, UserRole
from app.models.question_paper import QuestionPaper
from app.models.academic import Subject


def test_admin_unauthorized_access(client, student_headers, contributor_headers):
    # 1. Anonymous request
    res = client.get("/api/v1/admin/overview")
    assert res.status_code == 401

    # 2. Student request
    res = client.get("/api/v1/admin/overview", headers=student_headers)
    assert res.status_code == 403

    # 3. Contributor request
    res = client.get("/api/v1/admin/overview", headers=contributor_headers)
    assert res.status_code == 403


def test_admin_overview_metrics(client, admin_headers):
    res = client.get("/api/v1/admin/overview", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_users" in data
    assert "active_students" in data
    assert "total_contributors" in data
    assert "total_reviewers" in data
    assert "pending_submissions" in data
    assert "approved_papers" in data
    assert "verified_questions" in data
    assert "recent_activity" in data
    assert isinstance(data["recent_activity"], list)


def test_admin_user_management_and_guards(client, admin_headers, db):
    # 1. List users
    res = client.get("/api/v1/admin/users", headers=admin_headers)
    assert res.status_code == 200
    users = res.json()
    assert len(users) >= 4

    # 2. Get user profile
    res = client.get("/api/v1/admin/users/4", headers=admin_headers)
    assert res.status_code == 200
    profile = res.json()
    assert profile["id"] == 4

    # 3. Update user role (student -> contributor)
    res = client.patch("/api/v1/admin/users/4/role", json={"role": "contributor"}, headers=admin_headers)
    assert res.status_code == 200

    # 4. Attempt to demote the sole administrator -> expect 400
    res = client.patch("/api/v1/admin/users/1/role", json={"role": "student"}, headers=admin_headers)
    assert res.status_code == 400
    assert "last active administrator" in res.json()["detail"].lower()

    # 5. Attempt self-deactivation by admin -> expect 400
    res = client.patch("/api/v1/admin/users/1/status", json={"is_active": False}, headers=admin_headers)
    assert res.status_code == 400
    assert "cannot deactivate their own account" in res.json()["detail"].lower()

    # 6. Deactivate student account -> expect 200
    res = client.patch("/api/v1/admin/users/4/status", json={"is_active": False}, headers=admin_headers)
    assert res.status_code == 200

    # Restore student
    client.patch("/api/v1/admin/users/4/status", json={"is_active": True}, headers=admin_headers)
    client.patch("/api/v1/admin/users/4/role", json={"role": "student"}, headers=admin_headers)


def test_admin_question_paper_publishing(client, admin_headers, student_headers):
    # 1. List question papers
    res = client.get("/api/v1/admin/question-papers", headers=admin_headers)
    assert res.status_code == 200
    papers = res.json()
    assert len(papers) > 0
    paper_id = papers[0]["id"]

    # 2. Unpublish paper
    res = client.post(f"/api/v1/admin/question-papers/{paper_id}/unpublish", headers=admin_headers)
    assert res.status_code == 200

    # 3. Verify unpublished paper is not returned to student detail
    res_pub = client.get(f"/api/v1/pyqs/papers/{paper_id}")
    assert res_pub.status_code == 404

    # 4. Re-publish paper
    res = client.post(f"/api/v1/admin/question-papers/{paper_id}/publish", headers=admin_headers)
    assert res.status_code == 200

    # 5. Verify published paper is accessible
    res_pub = client.get(f"/api/v1/pyqs/papers/{paper_id}")
    assert res_pub.status_code == 200


def test_admin_contributors_and_reviewers(client, admin_headers):
    res_c = client.get("/api/v1/admin/contributors", headers=admin_headers)
    assert res_c.status_code == 200
    assert isinstance(res_c.json(), list)

    res_r = client.get("/api/v1/admin/reviewers", headers=admin_headers)
    assert res_r.status_code == 200
    assert isinstance(res_r.json(), list)


def test_admin_subject_and_syllabus(client, admin_headers):
    # List subjects
    res = client.get("/api/v1/admin/subjects", headers=admin_headers)
    assert res.status_code == 200

    # Create new subject
    new_sub = {
        "name": "Cloud Computing and Virtualization",
        "code": "CS-702-TEST",
        "branch_id": 1,
        "scheme_id": 1,
        "semester_number": 7,
        "credits": 4,
        "description": "Enterprise cloud systems",
    }
    res = client.post("/api/v1/admin/subjects", json=new_sub, headers=admin_headers)
    assert res.status_code == 201

    # Duplicate code attempt
    res_dup = client.post("/api/v1/admin/subjects", json=new_sub, headers=admin_headers)
    assert res_dup.status_code == 409

    # Coverage report
    res_cov = client.get("/api/v1/admin/syllabus/coverage", headers=admin_headers)
    assert res_cov.status_code == 200
    assert len(res_cov.json()) > 0


def test_admin_moderation_queue(client, admin_headers):
    res = client.get("/api/v1/admin/moderation/queue", headers=admin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_admin_announcements(client, admin_headers):
    # Create announcement
    announcement_data = {
        "title": "Semester Examination Timetable 2024",
        "content": "Official timetable published for Dec 2024 examinations on rgpv.ac.in",
        "audience": "all",
    }
    res = client.post("/api/v1/admin/announcements", json=announcement_data, headers=admin_headers)
    assert res.status_code == 201
    ann_id = res.json()["id"]

    # List announcements
    res_list = client.get("/api/v1/admin/announcements", headers=admin_headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # Delete announcement
    res_del = client.delete(f"/api/v1/admin/announcements/{ann_id}", headers=admin_headers)
    assert res_del.status_code == 200


def test_admin_audit_logs_and_health(client, admin_headers):
    # Audit logs
    res_logs = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert res_logs.status_code == 200
    assert isinstance(res_logs.json(), list)

    # System health diagnostics
    res_health = client.get("/api/v1/admin/system/health", headers=admin_headers)
    assert res_health.status_code == 200
    health_data = res_health.json()
    assert health_data["status"] == "operational"
    assert "database" in health_data
    assert "storage" in health_data
    # Ensure no secrets leaked
    assert "password" not in str(health_data).lower()
    assert "secret" not in str(health_data).lower()


def test_admin_analytics_export(client, admin_headers):
    # Overview
    res = client.get("/api/v1/admin/analytics/overview", headers=admin_headers)
    assert res.status_code == 200
    assert "user_roles" in res.json()

    # CSV Export
    res_csv = client.get("/api/v1/admin/analytics/export", headers=admin_headers)
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert "RGPV ExamMate - Platform Administration Report" in res_csv.text
