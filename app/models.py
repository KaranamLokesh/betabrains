from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(10), index=True)  # 'admin' or 'student'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User {}>".format(self.username)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String(10))
    subject = db.Column(db.String(50))
    question_text = db.Column(db.String(500))
    option_a = db.Column(db.String(100))
    option_b = db.Column(db.String(100))
    option_c = db.Column(db.String(100))
    option_d = db.Column(db.String(100))
    correct_answer = db.Column(db.String(1))  # 'a', 'b', 'c', or 'd'
    explanation = db.Column(db.String(500))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    author = db.relationship("User", backref=db.backref("questions", lazy="dynamic"))

    def __repr__(self):
        return "<Question {}>".format(self.question_text)


class StudentPerformance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    quiz_grade = db.Column(db.String(10))
    quiz_subject = db.Column(db.String(50))
    score = db.Column(db.Integer)
    total_questions = db.Column(db.Integer)

    student = db.relationship(
        "User", backref=db.backref("performances", lazy="dynamic")
    )

    def __repr__(self):
        return "<StudentPerformance {} - {} - {} - {}/{}".format(
            self.student.username,
            self.quiz_grade,
            self.quiz_subject,
            self.score,
            self.total_questions,
        )
