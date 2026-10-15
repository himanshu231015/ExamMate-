"""Tests for academic context, subjects, and syllabus structure."""

def test_get_universities_and_hierarchy(client):
    res = client.get("/api/v1/academic/universities")
    assert res.status_code == 200
    unis = res.json()
    assert len(unis) >= 1
    rgpv = next((u for u in unis if u["short_name"] == "RGPV"), None)
    assert rgpv is not None

    # Degrees
    deg_res = client.get(f"/api/v1/academic/universities/{rgpv['id']}/degrees")
    assert deg_res.status_code == 200
    degrees = deg_res.json()
    assert any(d["code"] == "B.Tech" for d in degrees)

    # Schemes
    sch_res = client.get(f"/api/v1/academic/universities/{rgpv['id']}/schemes")
    assert sch_res.status_code == 200
    schemes = sch_res.json()
    assert any(s["code"] == "CBGS" for s in schemes)


def test_get_subjects_and_syllabus(client):
    # Fetch subjects for Semester 3
    res = client.get("/api/v1/academic/subjects?semester=3")
    assert res.status_code == 200
    subjects = res.json()
    assert len(subjects) >= 1
    ds = next((s for s in subjects if s["code"] == "CS-301"), None)
    assert ds is not None
    assert ds["name"] == "Data Structures"

    # Fetch Syllabus for CS-301
    syl_res = client.get(f"/api/v1/academic/subjects/{ds['id']}/syllabus")
    assert syl_res.status_code == 200
    units = syl_res.json()
    assert len(units) >= 5  # RGPV 5 units
    u1 = units[0]
    assert "Unit I" in u1["title"]
    assert len(u1["topics"]) >= 1


def test_subject_authorization_protection(client, student_headers, admin_headers):
    # Student cannot create subject (Forbidden 403)
    new_sub = {
        "branch_id": 1,
        "scheme_id": 1,
        "name": "Unauthorized Subject",
        "code": "UN-999",
        "semester_number": 5,
        "credits": 3
    }
    stu_res = client.post("/api/v1/academic/subjects", json=new_sub, headers=student_headers)
    assert stu_res.status_code == 403

    # Admin can create subject
    admin_res = client.post("/api/v1/academic/subjects", json=new_sub, headers=admin_headers)
    assert admin_res.status_code == 201
    assert admin_res.json()["code"] == "UN-999"
