"""
Students blueprint – full CRUD for student records.
All endpoints require JWT authentication.
"""
import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.models.student import Student
from app.repositories.json_repository import JsonRepository
from app.services.student_service import StudentService
from app.services.student_service import DuplicateEmailError

students_bp = Blueprint("students", __name__)


def _get_service() -> StudentService:
    data_dir = current_app.config["DATA_DIR"]
    repo = JsonRepository[Student](os.path.join(data_dir, "students.json"), Student)
    return StudentService(repo)


@students_bp.route("", methods=["GET"])
@jwt_required()
def list_students():
    """List all students."""
    students = _get_service().list_students()
    return jsonify({"count": len(students), "students": students}), 200


@students_bp.route("/<string:student_id>", methods=["GET"])
@jwt_required()
def get_student(student_id: str):
    """Get a single student by ID."""
    student = _get_service().get_student(student_id)
    if student is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student), 200


@students_bp.route("", methods=["POST"])
@jwt_required()
def create_student():
    """Create a new student."""
    body = request.get_json(silent=True) or {}
    required_fields = ("first_name", "last_name", "email", "course")
    missing = [f for f in required_fields if not body.get(f, "").strip()]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        student = _get_service().create_student(body)
        return jsonify({"message": "Student created", "student": student}), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409


@students_bp.route("/<string:student_id>", methods=["PUT"])
@jwt_required()
def update_student(student_id: str):
    """Update an existing student."""
    body = request.get_json(silent=True) or {}
    try: 
        result = _get_service().update_student(student_id, body)
    except DuplicateEmailError as exc:
        return jsonify({"error": str(exc)}), 409
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    if result is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"message": "Student updated", "student": result}), 200


@students_bp.route("/<string:student_id>", methods=["DELETE"])
@jwt_required()
def delete_student(student_id: str):
    """Delete a student."""
    if _get_service().delete_student(student_id):
        return jsonify({"message": "Student deleted"}), 200
    return jsonify({"error": "Student not found"}), 404
