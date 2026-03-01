from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.student import Student
from app.models.user import User

student_bp = Blueprint("student", __name__, url_prefix="/students")


# ---------------- CREATE STUDENT ----------------
@student_bp.route("/", methods=["POST"])
@jwt_required()
def create_student():
    data = request.get_json()

    user_id = data.get("user_id")
    enrollment_no = data.get("enrollment_no")
    department = data.get("department")
    year = data.get("year")

    # Check if user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Check duplicate enrollment number
    if Student.query.filter_by(enrollment_no=enrollment_no).first():
        return jsonify({"message": "Enrollment number already exists"}), 400

    new_student = Student(
        user_id=user_id,
        enrollment_no=enrollment_no,
        department=department,
        year=year
    )

    db.session.add(new_student)
    db.session.commit()

    return jsonify({"message": "Student created successfully"}), 201


# ---------------- GET ALL STUDENTS ----------------
@student_bp.route("/", methods=["GET"])
@jwt_required()
def get_students():
    students = Student.query.all()

    result = []
    for student in students:
        result.append({
            "id": student.id,
            "name": student.user.name,
            "email": student.user.email,
            "enrollment_no": student.enrollment_no,
            "department": student.department,
            "year": student.year
        })

    return jsonify(result), 200


# ---------------- GET SINGLE STUDENT ----------------
@student_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_student(id):
    student = Student.query.get(id)

    if not student:
        return jsonify({"message": "Student not found"}), 404

    return jsonify({
        "id": student.id,
        "name": student.user.name,
        "email": student.user.email,
        "enrollment_no": student.enrollment_no,
        "department": student.department,
        "year": student.year
    }), 200


# ---------------- UPDATE STUDENT ----------------
@student_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_student(id):
    student = Student.query.get(id)

    if not student:
        return jsonify({"message": "Student not found"}), 404

    data = request.get_json()

    student.enrollment_no = data.get("enrollment_no", student.enrollment_no)
    student.department = data.get("department", student.department)
    student.year = data.get("year", student.year)

    db.session.commit()

    return jsonify({"message": "Student updated successfully"}), 200


# ---------------- DELETE STUDENT ----------------
@student_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_student(id):
    student = Student.query.get(id)

    if not student:
        return jsonify({"message": "Student not found"}), 404

    db.session.delete(student)
    db.session.commit()

    return jsonify({"message": "Student deleted successfully"}), 200