"""Tests for paper ingestion pipeline, reviewer governance, and duplicate detection."""

import io

def test_paper_submission_and_duplicate_detection(client, student_headers):
    # Create sample PDF content
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"

    files = {"file": ("rgpv_sample_paper.pdf", io.BytesIO(pdf_content), "application/pdf")}
    data = {
        "subject_id": 1,
        "scheme_id": 1,
        "exam_year": 2021,
        "exam_session": "December",
        "exam_type": "Main",
    }

    # 1. First submission succeeds
    res = client.post("/api/v1/submissions/", data=data, files=files, headers=student_headers)
    assert res.status_code == 201
    submission_data = res.json()
    assert submission_data["status"] == "pending"
    submission_id = submission_data["id"]

    # 2. Duplicate submission fails with 409 Conflict
    dup_files = {"file": ("rgpv_sample_paper.pdf", io.BytesIO(pdf_content), "application/pdf")}
    dup_res = client.post("/api/v1/submissions/", data=data, files=dup_files, headers=student_headers)
    assert dup_res.status_code == 409


def test_reviewer_governance_and_self_approval_prevention(client, student_headers, reviewer_headers):
    # Reviewer checks pending queue
    pending_res = client.get("/api/v1/submissions/pending", headers=reviewer_headers)
    assert pending_res.status_code == 200
    pending_list = pending_res.json()
    assert len(pending_list) >= 1
    sub_id = pending_list[0]["id"]

    # If the student (submitter) tries to approve: Forbidden 403 (wrong role)
    approve_payload = {"decision": "approved", "remarks": "Looks verified and authentic RGPV paper."}
    unauth_res = client.post(f"/api/v1/submissions/{sub_id}/review", json=approve_payload, headers=student_headers)
    assert unauth_res.status_code == 403

    # Reviewer approves submission
    rev_res = client.post(f"/api/v1/submissions/{sub_id}/review", json=approve_payload, headers=reviewer_headers)
    assert rev_res.status_code == 200
    assert "approved" in rev_res.json()["message"]


def test_contributor_reviewer_workflows_and_isolation(client, contributor_headers, reviewer_headers, student_headers):
    # 1. Contributor dashboard stats
    res_stats = client.get("/api/v1/submissions/stats/contributor", headers=contributor_headers)
    assert res_stats.status_code == 200
    assert "total_submissions" in res_stats.json()

    # 2. Reviewer dashboard stats
    res_rev_stats = client.get("/api/v1/submissions/stats/reviewer", headers=reviewer_headers)
    assert res_rev_stats.status_code == 200
    assert "pending_review" in res_rev_stats.json()

    # 3. Create a submission by contributor
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n% unique contributor test"
    files = {"file": ("contributor_paper.pdf", io.BytesIO(pdf_content), "application/pdf")}
    data = {
        "subject_id": 1,
        "scheme_id": 1,
        "exam_year": 2022,
        "exam_session": "June",
        "exam_type": "Main",
    }
    res_sub = client.post("/api/v1/submissions/", data=data, files=files, headers=contributor_headers)
    assert res_sub.status_code == 201
    sub_id = res_sub.json()["id"]

    # 4. Isolation test: Student user cannot view contributor's submission
    res_iso = client.get(f"/api/v1/submissions/{sub_id}", headers=student_headers)
    assert res_iso.status_code == 403

    # 5. Contributor can view their own submission
    res_own = client.get(f"/api/v1/submissions/{sub_id}", headers=contributor_headers)
    assert res_own.status_code == 200
    assert res_own.json()["id"] == sub_id

    # 6. Reviewer can flag submission
    res_flag = client.post(f"/api/v1/submissions/{sub_id}/flag", data={"reason": "Requires syllabus verification"}, headers=reviewer_headers)
    assert res_flag.status_code == 200

    # 7. Reviewer returns submission for correction
    res_corr = client.post(f"/api/v1/submissions/{sub_id}/review", json={"decision": "returned_for_correction", "remarks": "Re-upload with complete 5 units"}, headers=reviewer_headers)
    assert res_corr.status_code == 200

    # 8. Contributor resubmits
    res_resub = client.post(f"/api/v1/submissions/{sub_id}/resubmit", data={"notes": "Added complete unit details."}, headers=contributor_headers)
    assert res_resub.status_code == 200

