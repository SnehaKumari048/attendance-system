from app import db

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    teacher = db.relationship("User", backref="courses")