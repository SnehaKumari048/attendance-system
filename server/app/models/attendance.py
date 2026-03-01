from app import db
from datetime import date

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id"),
        nullable=False
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("course.id"),
        nullable=False
    )

    attendance_date = db.Column(
        db.Date,
        default=date.today,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False   # Present / Absent
    )

    student = db.relationship("Student", backref="attendances")
    course = db.relationship("Course", backref="attendances")