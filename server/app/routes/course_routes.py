from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.course import Course
from app.models.user import User

course_bp = Blueprint("course", __name__, url_prefix="/courses")


# ---------------- CREATE COURSE ----------------
@course_bp.route("/", methods=["POST"])
@jwt_required()
def create_course():
    data = request.get_json()

    name = data.get("name")
    code = data.get("code")
    teacher_id = data.get("teacher_id")

    teacher = User.query.get(teacher_id)
    if not teacher:
        return jsonify({"message": "Teacher not found"}), 404

    if Course.query.filter_by(code=code).first():
        return jsonify({"message": "Course code already exists"}), 400

    new_course = Course(
        name=name,
        code=code,
        teacher_id=teacher_id
    )

    db.session.add(new_course)
    db.session.commit()

    return jsonify({"message": "Course created successfully"}), 201


# ---------------- GET ALL COURSES ----------------
@course_bp.route("/", methods=["GET"])
@jwt_required()
def get_courses():
    courses = Course.query.all()

    result = []
    for course in courses:
        result.append({
            "id": course.id,
            "name": course.name,
            "code": course.code,
            "teacher_name": course.teacher.name
        })

    return jsonify(result), 200


# ---------------- GET SINGLE COURSE ----------------
@course_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_course(id):
    course = Course.query.get(id)

    if not course:
        return jsonify({"message": "Course not found"}), 404

    return jsonify({
        "id": course.id,
        "name": course.name,
        "code": course.code,
        "teacher_name": course.teacher.name
    }), 200


# ---------------- UPDATE COURSE ----------------
@course_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_course(id):
    course = Course.query.get(id)

    if not course:
        return jsonify({"message": "Course not found"}), 404

    data = request.get_json()

    course.name = data.get("name", course.name)
    course.code = data.get("code", course.code)

    db.session.commit()

    return jsonify({"message": "Course updated successfully"}), 200


# ---------------- DELETE COURSE ----------------
@course_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_course(id):
    course = Course.query.get(id)

    if not course:
        return jsonify({"message": "Course not found"}), 404

    db.session.delete(course)
    db.session.commit()

    return jsonify({"message": "Course deleted successfully"}), 200