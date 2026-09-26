"""
Student service – business logic for student CRUD.
"""

import uuid
from typing import Optional

from app.models.student import Student
from app.repositories.json_repository import JsonRepository

class DuplicateEmailError(ValueError):
    pass
class StudentService:
    def __init__(self, repo: JsonRepository[Student]) -> None:
        self._repo = repo

    def list_students(self) -> list[dict]:
        return [s.to_dict() for s in self._repo.get_all()]

    def get_student(self, student_id: str) -> Optional[dict]:
        student = self._repo.get_by_id(student_id)
        return student.to_dict() if student else None

    def create_student(self, data: dict) -> dict:
        # Check duplicate email
        if self._repo.get_by_field("email", data.get("email", "")):
            raise ValueError("A student with this email already exists")

        student = Student(
            id=str(uuid.uuid4()),
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            course=data["course"],
        )
        self._repo.create(student)
        return student.to_dict()

    def update_student(self, student_id: str, data: dict) -> Optional[dict]:
        existing = self._repo.get_by_id(student_id)
        if existing is None:
            return None
        if "email" in data:
            student_with_email = self._repo.get_by_field("email", data["email"])
            if student_with_email != None and  student_with_email.id != student_id:
                raise DuplicateEmailError("A student with this email already exists")
        if "is_active" in data and not isinstance(data["is_active"], bool):
            raise ValueError("is_active must be a boolean")

        updated = Student(
            id=student_id,
            first_name=data.get("first_name", existing.first_name),
            last_name=data.get("last_name", existing.last_name),
            email=data.get("email", existing.email),
            course=data.get("course", existing.course),
            enrollment_date=existing.enrollment_date,
            is_active=data.get("is_active", existing.is_active),
        )
        self._repo.update(student_id, updated)
        return updated.to_dict()

    def delete_student(self, student_id: str) -> bool:
        return self._repo.delete(student_id)
