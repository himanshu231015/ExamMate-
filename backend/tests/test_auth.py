"""Tests for user authentication, JWT tokens, and account deletion."""

def test_register_and_login_flow(client):
    # 1. Register new student
    register_payload = {
        "email": "newstudent@rgpvexammate.edu",
        "password": "Password@123",
        "full_name": "Test Student",
        "role": "student"
    }
    reg_res = client.post("/api/v1/auth/register", json=register_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == "newstudent@rgpvexammate.edu"

    # 2. Prevent duplicate email registration
    dup_res = client.post("/api/v1/auth/register", json=register_payload)
    assert dup_res.status_code == 400

    # 3. Login with credentials
    login_payload = {
        "email": "newstudent@rgpvexammate.edu",
        "password": "Password@123"
    }
    login_res = client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # 4. Access /me with token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "newstudent@rgpvexammate.edu"

    # 5. Login with invalid password fails
    bad_login = client.post(
        "/api/v1/auth/login",
        json={"email": "newstudent@rgpvexammate.edu", "password": "WrongPassword"}
    )
    assert bad_login.status_code == 401

    # 6. Delete account
    del_res = client.delete("/api/v1/auth/me", headers=headers)
    assert del_res.status_code == 200

    # 7. Login after deletion fails
    post_del_login = client.post("/api/v1/auth/login", json=login_payload)
    assert post_del_login.status_code == 401
