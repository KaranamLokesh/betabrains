from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512))
    role = db.Column(db.String(20), default="student")  # student or admin
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"), nullable=True)

    # Relationships
    questions = db.relationship("Question", backref="author", lazy="dynamic")
    performances = db.relationship(
        "StudentPerformance", backref="student", lazy="dynamic"
    )
    grade = db.relationship("Grade", backref="students")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(20), unique=True, nullable=False
    )  # e.g., "Grade 5", "Grade 6"
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subjects = db.relationship("Subject", backref="grade", lazy="dynamic")
    questions = db.relationship("Question", backref="grade_obj", lazy="dynamic")

    def __repr__(self):
        return f"<Grade {self.name}>"


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # e.g., "Mathematics", "Science"
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"), nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    questions = db.relationship("Question", backref="subject_obj", lazy="dynamic")

    def __repr__(self):
        return f"<Subject {self.name}>"


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String(20), nullable=False)  # Keep for backward compatibility
    subject = db.Column(
        db.String(50), nullable=False
    )  # Keep for backward compatibility
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # New foreign key relationships
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=True)
    uploaded_by = db.Column(
        db.String(64), nullable=True
    )  # Admin username or ID who uploaded via CSV
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=True)

    def __repr__(self):
        return f"<Question {self.id}: {self.question_text[:50]}...>"


class StudentPerformance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quiz_grade = db.Column(db.String(20), nullable=False)
    quiz_subject = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<StudentPerformance {self.student_id}: {self.score}/{self.total_questions}>"


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(64), nullable=True)

    grade = db.relationship("Grade", backref="quizzes")
    subject = db.relationship("Subject", backref="quizzes")
    questions = db.relationship("Question", backref="quiz", lazy="dynamic")

    def __repr__(self):
        return f"<Quiz {self.title} (Grade {self.grade_id}, Subject {self.subject_id})>"
