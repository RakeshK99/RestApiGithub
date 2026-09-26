"""
Tests for /api/v1/students endpoints.
"""

SAMPLE_STUDENT = {
    "first_name": "Alice",
    "last_name": "Smith",
    "email": "alice@example.com",
    "course": "Computer Science",
}


def test_create_student(client, auth_headers):
    resp = client.post("/api/v1/students", json=SAMPLE_STUDENT, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["student"]["email"] == "alice@example.com"


def test_list_students(client, auth_headers):
    client.post("/api/v1/students", json=SAMPLE_STUDENT, headers=auth_headers)
    resp = client.get("/api/v1/students", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["count"] >= 1


def test_get_student(client, auth_headers):
    create_resp = client.post("/api/v1/students", json={
        **SAMPLE_STUDENT, "email": "bob@example.com"
    }, headers=auth_headers)
    sid = create_resp.get_json()["student"]["id"]

    resp = client.get(f"/api/v1/students/{sid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == sid


def test_update_student(client, auth_headers):
    create_resp = client.post("/api/v1/students", json={
        **SAMPLE_STUDENT, "email": "charlie@example.com"
    }, headers=auth_headers)
    sid = create_resp.get_json()["student"]["id"]

    resp = client.put(f"/api/v1/students/{sid}", json={
        "course": "Mathematics"
    }, headers=auth_headers)
    assert resp.status_code == 200 
    assert resp.get_json()["student"]["course"] == "Mathematics"


def test_delete_student(client, auth_headers):
    create_resp = client.post("/api/v1/students", json={
        **SAMPLE_STUDENT, "email": "dave@example.com"
    }, headers=auth_headers)
    sid = create_resp.get_json()["student"]["id"]

    resp = client.delete(f"/api/v1/students/{sid}", headers=auth_headers)
    assert resp.status_code == 200

    resp = client.get(f"/api/v1/students/{sid}", headers=auth_headers)
    assert resp.status_code == 404
    
def test_update_student_active_status(client, auth_headers):
    create_resp = client.post("/api/v1/students", json={
        **SAMPLE_STUDENT, "email": "active@example.com"
    }, headers=auth_headers)

    sid = create_resp.get_json()["student"]["id"]

    resp = client.put(f"/api/v1/students/{sid}", json={
        "is_active": False
    }, headers=auth_headers)

    assert resp.status_code == 200
    assert resp.get_json()["student"]["is_active"] == False



def test_update_student_rejects_invalid_active_status(client, auth_headers):
    create_resp = client.post("/api/v1/students", json={
        **SAMPLE_STUDENT, "email": "invalid-active@example.com"
    }, headers=auth_headers)

    sid = create_resp.get_json()["student"]["id"]

    resp = client.put(f"/api/v1/students/{sid}", json={
        "is_active": "bananaa"
    }, headers=auth_headers)

    assert resp.status_code == 400

def test_update_student_not_found(client, auth_headers):
    resp = client.put(
        "/api/v1/students/nonexistent",
        json={"is_active": False},
        headers=auth_headers,
    )

    assert resp.status_code == 404

def test_update_student_reject_duplicate_email(client, auth_headers):
    create_resp = client.post("/api/v1/students", json={
        **SAMPLE_STUDENT, "email": "test1@gmail.com"
    }, headers=auth_headers)
    create_resp2 = client.post("/api/v1/students", json={
        **SAMPLE_STUDENT, "email": "test2@gmail.com"
    }, headers=auth_headers)
    sid = create_resp.get_json()["student"]["id"]
    bill = create_resp2.get_json()["student"]["id"]
    
    resp = client.put(f"/api/v1/students/{sid}", json={
        "email": "test2@gmail.com"
    }, headers=auth_headers)

    assert resp.status_code == 409
    check = client.get(f"/api/v1/students/{sid}", headers=auth_headers)
    assert check.get_json()["email"] == "test1@gmail.com"

def test_update_student_valid_email(client, auth_headers):
    create_resp = client.post("/api/v1/students", json={
        **SAMPLE_STUDENT, "email": "test3@gmail.com"
    }, headers=auth_headers)
    sid = create_resp.get_json()["student"]["id"]
    resp = client.put(f"/api/v1/students/{sid}", json={
        "email": "another@gmail.com"
    }, headers=auth_headers)
    assert resp.status_code == 200;
    assert resp.get_json()["student"]["email"] == "another@gmail.com"

def test_update_student_same_email(client, auth_headers):
    create_resp = client.post("/api/v1/students", json={
        **SAMPLE_STUDENT, "email": "test4@gmail.com"
    }, headers=auth_headers)
    jill = create_resp.get_json()["student"]["id"]
    resp = client.put(f"/api/v1/students/{jill}", json={
        "email": "test4@gmail.com"
    }, headers=auth_headers)
    assert resp.status_code == 200;
    assert resp.get_json()["student"]["email"] == "test4@gmail.com"


def test_students_require_auth(client):
    resp = client.get("/api/v1/students")
    assert resp.status_code == 401

