from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    role = SelectField(
        "Role",
        choices=[("student", "Student"), ("admin", "Admin")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")


class QuestionForm(FlaskForm):
    grade = StringField("Grade", validators=[DataRequired()])
    subject = StringField("Subject", validators=[DataRequired()])
    question_text = StringField("Question", validators=[DataRequired()])
    option_a = StringField("Option A", validators=[DataRequired()])
    option_b = StringField("Option B", validators=[DataRequired()])
    option_c = StringField("Option C", validators=[DataRequired()])
    option_d = StringField("Option D", validators=[DataRequired()])
    correct_answer = SelectField(
        "Correct Answer",
        choices=[("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")],
        validators=[DataRequired()],
    )
    explanation = StringField("Explanation", validators=[DataRequired()])
    submit = SubmitField("Submit")


class QuizForm(FlaskForm):
    submit = SubmitField("Submit Answers")


class PracticeForm(FlaskForm):
    question = StringField("Ask a question", validators=[DataRequired()])
    submit = SubmitField("Ask")


class PerformanceFilterForm(FlaskForm):
    search = StringField("Search (Quiz ID, Subject, or Grade)", validators=[])
    subject = SelectField(
        "Subject", choices=[("all", "All Subjects")], validators=[DataRequired()]
    )
    grade = SelectField(
        "Grade", choices=[("all", "All Grades")], validators=[DataRequired()]
    )
    sort_by = SelectField(
        "Sort By",
        choices=[
            ("date_desc", "Date (Newest First)"),
            ("date_asc", "Date (Oldest First)"),
            ("score_desc", "Score (Highest First)"),
            ("score_asc", "Score (Lowest First)"),
            ("subject", "Subject"),
            ("grade", "Grade"),
        ],
        validators=[DataRequired()],
    )
    show_only = SelectField(
        "Show Only",
        choices=[
            ("all", "All Attempts"),
            ("recent", "Last 5 Attempts"),
            ("best", "Best Scores"),
            ("worst", "Lowest Scores"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Apply Filters")


class ChatForm(FlaskForm):
    message = StringField(
        "Ask me anything about your quiz or studies...", validators=[DataRequired()]
    )
    submit = SubmitField("Send")
