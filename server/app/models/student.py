from app import db

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    enrollment_no = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100))
    year = db.Column(db.Integer)

    user = db.relationship("User", backref="student_profile")