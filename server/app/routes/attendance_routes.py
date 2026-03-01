from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.course import Course
from datetime import datetime
from app import socketio
from flask_jwt_extended import get_jwt_identity
from app.models.user import User


attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")


# ---------------- MARK ATTENDANCE ----------------
@attendance_bp.route("/mark", methods=["POST"])
@jwt_required()
def mark_attendance():

    # Get current logged in user
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))

    # Only teacher can mark attendance
    if user.role != "teacher":
        return jsonify({"message": "Only teachers can mark attendance"}), 403

    data = request.get_json()

    student_id = data.get("student_id")
    course_id = data.get("course_id")
    status = data.get("status")

    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"message": "Course not found"}), 404

    today = datetime.today().date()

    existing = Attendance.query.filter_by(
        student_id=student_id,
        course_id=course_id,
        attendance_date=today
    ).first()

    if existing:
        return jsonify({"message": "Attendance already marked today"}), 400

    new_attendance = Attendance(
        student_id=student_id,
        course_id=course_id,
        status=status,
        attendance_date=today
    )

    db.session.add(new_attendance)
    db.session.commit()

    socketio.emit("attendance_update", {
        "student": student.user.name,
        "course": course.name,
        "status": status
    })

    return jsonify({"message": "Attendance marked successfully"}), 201

# ---------------- GET ATTENDANCE BY STUDENT ----------------
@attendance_bp.route("/student/<int:student_id>", methods=["GET"])
@jwt_required()
def get_attendance_by_student(student_id):
    records = Attendance.query.filter_by(student_id=student_id).all()

    result = []
    for record in records:
        result.append({
            "course": record.course.name,
            "date": record.attendance_date,
            "status": record.status
        })

    return jsonify(result), 200


# ---------------- GET ATTENDANCE BY COURSE ----------------
@attendance_bp.route("/course/<int:course_id>", methods=["GET"])
@jwt_required()
def get_attendance_by_course(course_id):
    records = Attendance.query.filter_by(course_id=course_id).all()

    result = []
    for record in records:
        result.append({
            "student": record.student.user.name,
            "date": record.attendance_date,
            "status": record.status
        })

    return jsonify(result), 200

# ---------------- ATTENDANCE PERCENTAGE ----------------
@attendance_bp.route("/percentage/<int:student_id>/<int:course_id>", methods=["GET"])
@jwt_required()
def attendance_percentage(student_id, course_id):

    # Check student exists
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404

    # Check course exists
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"message": "Course not found"}), 404

    records = Attendance.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).all()

    if not records:
        return jsonify({
            "message": "No attendance records found",
            "percentage": 0
        }), 200

    total_classes = len(records)
    present_count = sum(1 for r in records if r.status.lower() == "present")

    percentage = (present_count / total_classes) * 100
    percentage = round(percentage, 2)


    response = {
        "student": student.user.name,
        "course": course.name,
        "total_classes": total_classes,
        "present": present_count,
        "percentage": percentage
    }

    #  Low attendance warning
    if percentage < 75:
        response["warning"] = "Attendance below 75%"

        socketio.emit("low_attendance_warning", {
            "student": student.user.name,
            "course": course.name,
            "percentage": percentage
        })

    return jsonify(response), 200




# ---------------- COURSE SUMMARY DASHBOARD ----------------
@attendance_bp.route("/course-summary/<int:course_id>", methods=["GET"])
@jwt_required()
def course_summary(course_id):

    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))

    # Only teachers allowed
    if user.role != "teacher":
        return jsonify({"message": "Only teachers can view course summary"}), 403

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"message": "Course not found"}), 404

    students = Student.query.all()

    summary = []
    below_75 = 0
    total_percentage = 0
    counted_students = 0

    for student in students:
        records = Attendance.query.filter_by(
            student_id=student.id,
            course_id=course_id
        ).all()

        if not records:
            continue

        total_classes = len(records)
        present_count = sum(1 for r in records if r.status.lower() == "present")
        percentage = (present_count / total_classes) * 100

        counted_students += 1
        total_percentage += percentage

        if percentage < 75:
            below_75 += 1

        summary.append({
            "student": student.user.name,
            "percentage": round(percentage, 2)
        })

    course_average = round(total_percentage / counted_students, 2) if counted_students > 0 else 0

    return jsonify({
        "course": course.name,
        "total_students_with_records": counted_students,
        "below_75_percent": below_75,
        "course_average": course_average,
        "students": summary
    }), 200