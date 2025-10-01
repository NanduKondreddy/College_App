from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)   # increased length
    role = db.Column(db.String(20), nullable=False)  # admin/faculty

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Stream(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    courses = db.relationship(
        "Course", backref="stream", cascade="all, delete-orphan"
    )

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    stream_id = db.Column(
        db.Integer, db.ForeignKey("stream.id"), nullable=False
    )
    semesters = db.relationship(
        "Semester", backref="course", cascade="all, delete-orphan"
    )

class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, default=0)
    course_id = db.Column(
        db.Integer, db.ForeignKey("course.id"), nullable=False
    )
