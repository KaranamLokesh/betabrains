import csv
from datetime import datetime, timedelta
from io import TextIOWrapper

from flask import flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from openai import OpenAI

from app import app, db
from app.forms import (
    ChatForm,
    GradeForm,
    LoginForm,
    PerformanceFilterForm,
    PracticeForm,
    QuestionForm,
    QuizForm,
    RegistrationForm,
    StudentAssignmentForm,
    SubjectForm,
)
from app.models import Grade, Question, StudentPerformance, Subject, User


@app.route("/")
@app.route("/index")
@login_required
def index():
    if hasattr(current_user, "role"):
        if current_user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        elif current_user.role == "student":
            return redirect(url_for("student_dashboard"))
    # fallback for users with no or invalid role
    logout_user()
    flash("Invalid user role. Please log in again.")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        else:
            return redirect(url_for("student_dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        if user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        else:
            return redirect(url_for("student_dashboard"))
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data, email=form.email.data, role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/student/dashboard")
@login_required
def student_dashboard():
    if not hasattr(current_user, "role") or current_user.role != "student":
        logout_user()
        flash("Access denied. Please log in as a student.")
        return redirect(url_for("login"))
    return render_template("student_dashboard.html", title="Student Dashboard")


@app.route("/student/performance")
@login_required
def view_performance():
    if not hasattr(current_user, "role") or current_user.role != "student":
        logout_user()
        flash("Access denied. Please log in as a student.")
        return redirect(url_for("login"))

    form = PerformanceFilterForm()

    # Get all subjects and grades for the dropdowns
    subjects = (
        db.session.query(StudentPerformance.quiz_subject)
        .filter_by(student_id=current_user.id)
        .distinct()
        .all()
    )
    grades = (
        db.session.query(StudentPerformance.quiz_grade)
        .filter_by(student_id=current_user.id)
        .distinct()
        .all()
    )

    subject_choices = [("all", "All Subjects")] + [
        (subject[0], subject[0]) for subject in subjects
    ]
    grade_choices = [("all", "All Grades")] + [
        (grade[0], f"Grade {grade[0]}") for grade in grades
    ]

    form.subject.choices = subject_choices
    form.grade.choices = grade_choices

    # Get filter parameters from GET request
    selected_subject = request.args.get("subject", "all")
    selected_grade = request.args.get("grade", "all")
    selected_sort = request.args.get("sort_by", "date_desc")
    selected_show = request.args.get("show_only", "all")
    search_term = request.args.get("search", "").strip()

    # Set form defaults
    form.subject.data = selected_subject
    form.grade.data = selected_grade
    form.sort_by.data = selected_sort
    form.show_only.data = selected_show
    form.search.data = search_term

    # Get all past performances for this student
    query = StudentPerformance.query.filter_by(student_id=current_user.id)

    # Apply search filter with exact matching
    if search_term:
        # For numeric search, look for exact ID match
        if search_term.isdigit():
            query = query.filter(StudentPerformance.id == int(search_term))
        else:
            # For text search, use exact matching or word boundaries
            search_term_lower = search_term.lower()
            query = query.filter(
                db.or_(
                    StudentPerformance.quiz_subject.ilike(f"{search_term_lower}"),
                    StudentPerformance.quiz_subject.ilike(f"{search_term_lower} %"),
                    StudentPerformance.quiz_subject.ilike(f"% {search_term_lower}"),
                    StudentPerformance.quiz_subject.ilike(f"% {search_term_lower} %"),
                    StudentPerformance.quiz_grade.ilike(f"{search_term_lower}"),
                    StudentPerformance.quiz_grade.ilike(f"{search_term_lower} %"),
                    StudentPerformance.quiz_grade.ilike(f"% {search_term_lower}"),
                    StudentPerformance.quiz_grade.ilike(f"% {search_term_lower} %"),
                )
            )

    # Apply subject filter
    if selected_subject and selected_subject != "all":
        query = query.filter_by(quiz_subject=selected_subject)

    # Apply grade filter
    if selected_grade and selected_grade != "all":
        query = query.filter_by(quiz_grade=selected_grade)

    # Apply "show only" filter
    if selected_show == "recent":
        query = query.order_by(StudentPerformance.id.desc()).limit(5)
    elif selected_show == "best":
        query = query.order_by(StudentPerformance.score.desc())
    elif selected_show == "worst":
        query = query.order_by(StudentPerformance.score.asc())

    # Apply sorting (only if not already sorted by show_only)
    if selected_show not in ["recent", "best", "worst"]:
        if selected_sort == "date_desc":
            query = query.order_by(StudentPerformance.id.desc())
        elif selected_sort == "date_asc":
            query = query.order_by(StudentPerformance.id.asc())
        elif selected_sort == "score_desc":
            query = query.order_by(StudentPerformance.score.desc())
        elif selected_sort == "score_asc":
            query = query.order_by(StudentPerformance.score.asc())
        elif selected_sort == "subject":
            query = query.order_by(
                StudentPerformance.quiz_subject, StudentPerformance.id.desc()
            )
        elif selected_sort == "grade":
            query = query.order_by(
                StudentPerformance.quiz_grade, StudentPerformance.id.desc()
            )

    performances = query.all()

    # For each performance, get the questions and create a detailed view
    performance_details = []
    total_score = 0
    total_questions = 0
    best_percentage = 0

    for performance in performances:
        questions = Question.query.filter_by(
            grade=performance.quiz_grade, subject=performance.quiz_subject
        ).all()
        percentage = (
            (performance.score / performance.total_questions * 100)
            if performance.total_questions > 0
            else 0
        )

        # Update statistics
        total_score += performance.score
        total_questions += performance.total_questions
        if percentage > best_percentage:
            best_percentage = percentage

        performance_details.append(
            {
                "performance": performance,
                "questions": questions,
                "percentage": percentage,
            }
        )

    # Calculate average score
    avg_score = (total_score * 100 / total_questions) if total_questions > 0 else 0

    return render_template(
        "performance.html",
        title="My Performance",
        performance_details=performance_details,
        form=form,
        avg_score=avg_score,
        best_percentage=best_percentage,
    )


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return redirect(url_for("index"))

    # Get all questions
    questions = Question.query.all()

    # Get all students
    students = User.query.filter_by(role="student").all()

    # Get all performances
    performances = StudentPerformance.query.all()

    # Get unique grades and subjects for navigation
    grades = db.session.query(Question.grade).distinct().all()
    subjects = db.session.query(Question.subject).distinct().all()

    # Calculate basic statistics
    total_students = len(students)
    total_questions = len(questions)
    total_attempts = len(performances)

    # Calculate average performance
    if performances:
        total_score = sum(p.score for p in performances)
        total_possible = sum(p.total_questions for p in performances)
        avg_performance = (
            (total_score / total_possible * 100) if total_possible > 0 else 0
        )
    else:
        avg_performance = 0

    # Get top performing students (top 5)
    top_students = (
        db.session.query(
            User.username,
            StudentPerformance.student_id,
            db.func.avg(
                StudentPerformance.score * 100.0 / StudentPerformance.total_questions
            ).label("avg_score"),
            db.func.count(StudentPerformance.id).label("attempts"),
        )
        .join(StudentPerformance, User.id == StudentPerformance.student_id)
        .group_by(User.id, User.username, StudentPerformance.student_id)
        .order_by(
            db.func.avg(
                StudentPerformance.score * 100.0 / StudentPerformance.total_questions
            ).desc()
        )
        .limit(5)
        .all()
    )

    # Get recent activity (last 10 attempts)
    recent_attempts = (
        StudentPerformance.query.join(User, StudentPerformance.student_id == User.id)
        .order_by(
            StudentPerformance.timestamp.desc()
            if StudentPerformance.timestamp
            else StudentPerformance.id.desc()
        )
        .limit(10)
        .all()
    )

    # Get performance by subject (top 5)
    subject_performance = (
        db.session.query(
            StudentPerformance.quiz_subject,
            db.func.avg(
                StudentPerformance.score * 100.0 / StudentPerformance.total_questions
            ).label("avg_score"),
            db.func.count(StudentPerformance.id).label("attempts"),
        )
        .group_by(StudentPerformance.quiz_subject)
        .order_by(
            db.func.avg(
                StudentPerformance.score * 100.0 / StudentPerformance.total_questions
            ).desc()
        )
        .limit(5)
        .all()
    )

    # Get performance by grade (top 5)
    grade_performance = (
        db.session.query(
            StudentPerformance.quiz_grade,
            db.func.avg(
                StudentPerformance.score * 100.0 / StudentPerformance.total_questions
            ).label("avg_score"),
            db.func.count(StudentPerformance.id).label("attempts"),
        )
        .group_by(StudentPerformance.quiz_grade)
        .order_by(
            db.func.avg(
                StudentPerformance.score * 100.0 / StudentPerformance.total_questions
            ).desc()
        )
        .limit(5)
        .all()
    )

    return render_template(
        "admin_dashboard.html",
        title="Admin Dashboard",
        questions=questions,
        students=students,
        grades=grades,
        subjects=subjects,
        top_students=top_students,
        recent_attempts=recent_attempts,
        subject_performance=subject_performance,
        grade_performance=grade_performance,
        total_students=total_students,
        total_questions=total_questions,
        total_attempts=total_attempts,
        avg_performance=avg_performance,
    )


@app.route("/admin/add_question", methods=["GET", "POST"])
@login_required
def add_question():
    if current_user.role != "admin":
        return redirect(url_for("index"))

    form = QuestionForm()

    # Populate grade and subject choices
    grades = Grade.query.all()
    form.grade.choices = [(grade.name, grade.name) for grade in grades]

    # Get subjects for the selected grade (will be populated via AJAX or on form load)
    subjects = Subject.query.all()
    form.subject.choices = [(subject.name, subject.name) for subject in subjects]

    if form.validate_on_submit():
        question = Question(
            grade=form.grade.data,
            subject=form.subject.data,
            question_text=form.question_text.data,
            option_a=form.option_a.data,
            option_b=form.option_b.data,
            option_c=form.option_c.data,
            option_d=form.option_d.data,
            correct_answer=form.correct_answer.data,
            explanation=form.explanation.data,
            author_id=current_user.id,
        )
        db.session.add(question)
        db.session.commit()
        flash("Question has been added.")
        return redirect(url_for("admin_dashboard"))

    return render_template("add_question.html", title="Add Question", form=form)


@app.route("/admin/manage_grades", methods=["GET", "POST"])
@login_required
def manage_grades():
    if current_user.role != "admin":
        return redirect(url_for("index"))

    form = GradeForm()
    if form.validate_on_submit():
        grade = Grade(name=form.name.data, description=form.description.data)
        db.session.add(grade)
        db.session.commit()
        flash(f"Grade '{form.name.data}' has been added.")
        return redirect(url_for("manage_grades"))

    grades = Grade.query.all()
    return render_template(
        "admin_manage_grades.html", title="Manage Grades", form=form, grades=grades
    )


@app.route("/admin/manage_subjects", methods=["GET", "POST"])
@login_required
def manage_subjects():
    if current_user.role != "admin":
        return redirect(url_for("index"))

    form = SubjectForm()

    # Populate grade choices
    grades = Grade.query.all()
    form.grade.choices = [(grade.id, grade.name) for grade in grades]

    if form.validate_on_submit():
        subject = Subject(
            name=form.name.data,
            grade_id=form.grade.data,
            description=form.description.data,
        )
        db.session.add(subject)
        db.session.commit()
        flash(f"Subject '{form.name.data}' has been added.")
        return redirect(url_for("manage_subjects"))

    subjects = Subject.query.all()
    return render_template(
        "admin_manage_subjects.html",
        title="Manage Subjects",
        form=form,
        subjects=subjects,
    )


@app.route("/admin/manage_questions")
@login_required
def manage_questions():
    if current_user.role != "admin":
        return redirect(url_for("index"))

    # Get all questions with author information
    questions = (
        Question.query.join(User, Question.author_id == User.id)
        .order_by(Question.created_at.desc())
        .all()
    )

    return render_template(
        "admin_manage_questions.html", title="Manage Questions", questions=questions
    )


@app.route("/admin/manage_students", methods=["GET", "POST"])
@login_required
def manage_students():
    if current_user.role != "admin":
        return redirect(url_for("index"))

    form = StudentAssignmentForm()

    # Populate student and grade choices
    students = User.query.filter_by(role="student").all()
    form.student.choices = [
        (student.id, f"{student.username} ({student.email})") for student in students
    ]

    grades = Grade.query.all()
    form.grade.choices = [(grade.id, grade.name) for grade in grades]

    if form.validate_on_submit():
        student = User.query.get(form.student.data)
        student.grade_id = form.grade.data
        db.session.commit()
        flash(
            f"Student '{student.username}' has been assigned to {student.grade.name}."
        )
        return redirect(url_for("manage_students"))

    students_with_grades = User.query.filter_by(role="student").all()
    return render_template(
        "admin_manage_students.html",
        title="Manage Students",
        form=form,
        students=students_with_grades,
    )


@app.route("/quiz/select")
@login_required
def select_quiz():
    if current_user.role != "student":
        return redirect(url_for("index"))
    quizzes = db.session.query(Question.grade, Question.subject).distinct().all()
    return render_template("select_quiz.html", title="Select a Quiz", quizzes=quizzes)


@app.route("/quiz/<grade>/<subject>", methods=["GET", "POST"])
@login_required
def take_quiz(grade, subject):
    if current_user.role != "student":
        return redirect(url_for("index"))

    questions = Question.query.filter_by(grade=grade, subject=subject).all()
    form = QuizForm()

    if form.validate_on_submit():
        score = 0
        user_answers = {}
        for question in questions:
            user_answer = request.form.get(f"question_{question.id}")
            user_answers[question.id] = user_answer
            if user_answer == question.correct_answer:
                score += 1

        performance = StudentPerformance(
            student_id=current_user.id,
            quiz_grade=grade,
            quiz_subject=subject,
            score=score,
            total_questions=len(questions),
        )
        db.session.add(performance)
        db.session.commit()
        session["user_answers"] = user_answers

        return redirect(url_for("quiz_results", performance_id=performance.id))

    return render_template(
        "quiz.html",
        title="Quiz",
        grade=grade,
        subject=subject,
        questions=questions,
        form=form,
    )


@app.route("/quiz/results/<int:performance_id>")
@login_required
def quiz_results(performance_id):
    performance = StudentPerformance.query.get_or_404(performance_id)

    # Check if current user is admin or the student who took the quiz
    is_admin = current_user.role == "admin"
    is_own_quiz = current_user.id == performance.student_id

    if is_admin:
        # For admin users, show view-only mode without user answers
        user_answers = {}
        view_mode = "admin"
    else:
        # For students, get their actual answers from session
        user_answers = session.get("user_answers", {})
        view_mode = "student"

    questions = Question.query.filter_by(
        grade=performance.quiz_grade, subject=performance.quiz_subject
    ).all()

    return render_template(
        "results.html",
        title="Quiz Results",
        performance=performance,
        questions=questions,
        user_answers=user_answers,
        view_mode=view_mode,
        is_admin=is_admin,
    )


@app.route("/practice", methods=["GET", "POST"])
@login_required
def practice():
    form = PracticeForm()
    answer = None
    if form.validate_on_submit():
        try:
            client = OpenAI(api_key=app.config["OPENAI_API_KEY"])
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful tutor."},
                    {"role": "user", "content": form.question.data},
                ],
            )
            answer = response.choices[0].message.content
        except Exception as e:
            flash(f"Error: {e}")
    return render_template("practice.html", title="Practice", form=form, answer=answer)


@app.route("/student/chat", methods=["GET", "POST"])
@login_required
def chat_with_tutor():
    if not hasattr(current_user, "role") or current_user.role != "student":
        logout_user()
        flash("Access denied. Please log in as a student.")
        return redirect(url_for("login"))

    form = ChatForm()

    # Get question context if provided
    question_id = request.args.get("question_id")
    context_type = request.args.get("context", "general")
    current_question = None

    if question_id:
        current_question = Question.query.get(question_id)
        # Clear chat history for question-specific help to start fresh
        session.pop("chat_history", None)
        chat_history = []
    else:
        chat_history = session.get("chat_history", [])

    if form.validate_on_submit():
        # Build context based on the situation
        if current_question and context_type == "quiz":
            # Context for specific question during quiz
            context = f"""You are a helpful tutor helping a student with a specific question during a quiz.

Current Question:
Question: {current_question.question_text}
Options:
A: {current_question.option_a}
B: {current_question.option_b}
C: {current_question.option_c}
D: {current_question.option_d}
Correct Answer: {current_question.correct_answer.upper()}
Explanation: {current_question.explanation}

The student is asking for help with this specific question. Provide helpful guidance without giving away the answer directly. Encourage critical thinking and explain the concepts involved."""
        else:
            # General context with recent performance
            recent_performances = (
                StudentPerformance.query.filter_by(student_id=current_user.id)
                .order_by(StudentPerformance.id.desc())
                .limit(3)
                .all()
            )

            context = "You are a helpful tutor. The student has recently taken these quizzes:\n"
            for perf in recent_performances:
                questions = Question.query.filter_by(
                    grade=perf.quiz_grade, subject=perf.quiz_subject
                ).all()
                context += f"\n{perf.quiz_grade} Grade {perf.quiz_subject}: {perf.score}/{perf.total_questions} correct\n"
                for q in questions:
                    context += f"- Question: {q.question_text}\n  Correct Answer: {q.correct_answer.upper()}\n  Explanation: {q.explanation}\n"

        # Add chat history for context (only for general chat, not question-specific)
        if not current_question and chat_history:
            context += "\n\nRecent conversation:\n"
            for msg in chat_history[-6:]:  # Last 6 messages for context
                context += f"{msg['role']}: {msg['content']}\n"

        try:
            client = OpenAI(api_key=app.config["OPENAI_API_KEY"])
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": context
                        + "\n\nYou are a helpful tutor. Answer the student's question based on their quiz performance and provide clear explanations. Be encouraging and educational.",
                    },
                    {"role": "user", "content": form.message.data},
                ],
                max_tokens=500,
            )

            ai_response = response.choices[0].message.content

            # Add to chat history
            chat_history.append({"role": "user", "content": form.message.data})
            chat_history.append({"role": "assistant", "content": ai_response})

            # Keep only last 10 messages to avoid token limits
            if len(chat_history) > 10:
                chat_history = chat_history[-10:]

            session["chat_history"] = chat_history

            return render_template(
                "chat.html",
                title="Chat with AI Tutor",
                form=form,
                chat_history=chat_history,
                current_question=current_question,
                context_type=context_type,
            )

        except Exception as e:
            flash(f"Error: {e}")
            return render_template(
                "chat.html",
                title="Chat with AI Tutor",
                form=form,
                chat_history=chat_history,
                current_question=current_question,
                context_type=context_type,
            )

    return render_template(
        "chat.html",
        title="Chat with AI Tutor",
        form=form,
        chat_history=chat_history,
        current_question=current_question,
        context_type=context_type,
    )


@app.route("/student/clear_chat")
@login_required
def clear_chat():
    session.pop("chat_history", None)
    flash("Chat history cleared.")
    return redirect(url_for("chat_with_tutor"))


@app.route("/admin/student/<int:student_id>/performance")
@login_required
def admin_view_student_performance(student_id):
    if current_user.role != "admin":
        return redirect(url_for("index"))

    # Get the student
    student = User.query.get_or_404(student_id)
    if student.role != "student":
        flash("Invalid student ID.")
        return redirect(url_for("admin_dashboard"))

    # Get filter parameters
    selected_subject = request.args.get("subject", "all")
    selected_grade = request.args.get("grade", "all")
    selected_sort = request.args.get("sort_by", "date_desc")

    # Get all subjects and grades for the dropdowns
    subjects = (
        db.session.query(StudentPerformance.quiz_subject)
        .filter_by(student_id=student_id)
        .distinct()
        .all()
    )
    grades = (
        db.session.query(StudentPerformance.quiz_grade)
        .filter_by(student_id=student_id)
        .distinct()
        .all()
    )

    subject_choices = [("all", "All Subjects")] + [
        (subject[0], subject[0]) for subject in subjects
    ]
    grade_choices = [("all", "All Grades")] + [
        (grade[0], f"Grade {grade[0]}") for grade in grades
    ]

    # Get all past performances for this student
    query = StudentPerformance.query.filter_by(student_id=student_id)

    # Apply subject filter
    if selected_subject and selected_subject != "all":
        query = query.filter_by(quiz_subject=selected_subject)

    # Apply grade filter
    if selected_grade and selected_grade != "all":
        query = query.filter_by(quiz_grade=selected_grade)

    # Apply sorting
    if selected_sort == "date_desc":
        query = query.order_by(StudentPerformance.id.desc())
    elif selected_sort == "date_asc":
        query = query.order_by(StudentPerformance.id.asc())
    elif selected_sort == "score_desc":
        query = query.order_by(StudentPerformance.score.desc())
    elif selected_sort == "score_asc":
        query = query.order_by(StudentPerformance.score.asc())
    elif selected_sort == "subject":
        query = query.order_by(
            StudentPerformance.quiz_subject, StudentPerformance.id.desc()
        )
    elif selected_sort == "grade":
        query = query.order_by(
            StudentPerformance.quiz_grade, StudentPerformance.id.desc()
        )

    performances = query.all()

    # Calculate statistics
    total_attempts = len(performances)
    if performances:
        total_score = sum(p.score for p in performances)
        total_questions = sum(p.total_questions for p in performances)
        avg_score = (total_score * 100 / total_questions) if total_questions > 0 else 0
        best_performance = max(
            performances,
            key=lambda p: p.score / p.total_questions if p.total_questions > 0 else 0,
        )
        best_percentage = (
            (best_performance.score / best_performance.total_questions * 100)
            if best_performance.total_questions > 0
            else 0
        )
    else:
        avg_score = 0
        best_percentage = 0
        best_performance = None

    # Get performance by subject
    subject_performance = (
        db.session.query(
            StudentPerformance.quiz_subject,
            db.func.avg(
                StudentPerformance.score * 100.0 / StudentPerformance.total_questions
            ).label("avg_score"),
            db.func.count(StudentPerformance.id).label("attempts"),
        )
        .filter_by(student_id=student_id)
        .group_by(StudentPerformance.quiz_subject)
        .order_by(
            db.func.avg(
                StudentPerformance.score * 100.0 / StudentPerformance.total_questions
            ).desc()
        )
        .all()
    )

    # Get performance by grade
    grade_performance = (
        db.session.query(
            StudentPerformance.quiz_grade,
            db.func.avg(
                StudentPerformance.score * 100.0 / StudentPerformance.total_questions
            ).label("avg_score"),
            db.func.count(StudentPerformance.id).label("attempts"),
        )
        .filter_by(student_id=student_id)
        .group_by(StudentPerformance.quiz_grade)
        .order_by(StudentPerformance.quiz_grade)
        .all()
    )

    return render_template(
        "admin_student_performance.html",
        title=f"Student Performance - {student.username}",
        student=student,
        performances=performances,
        subject_choices=subject_choices,
        grade_choices=grade_choices,
        subject_performance=subject_performance,
        grade_performance=grade_performance,
        total_attempts=total_attempts,
        avg_score=avg_score,
        best_percentage=best_percentage,
        best_performance=best_performance,
        selected_subject=selected_subject,
        selected_grade=selected_grade,
        selected_sort=selected_sort,
    )


@app.route("/admin/update_timestamps")
@login_required
def update_timestamps():
    if current_user.role != "admin":
        return redirect(url_for("index"))

    # Get all performances without timestamps, ordered by ID
    performances = (
        StudentPerformance.query.filter_by(timestamp=None)
        .order_by(StudentPerformance.id)
        .all()
    )

    if performances:
        # Set timestamps starting from 7 days ago, with 1 hour intervals
        base_time = datetime.utcnow() - timedelta(days=7)

        for i, performance in enumerate(performances):
            # Add hours based on ID to simulate different times
            performance.timestamp = base_time + timedelta(hours=i)

        db.session.commit()
        flash(f"Updated {len(performances)} records with timestamps.")
    else:
        flash("All records already have timestamps.")

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/students")
@login_required
def admin_students():
    if current_user.role != "admin":
        return redirect(url_for("index"))

    # Get filter parameters
    selected_grade = request.args.get("grade", "all")
    selected_subject = request.args.get("subject", "all")
    search_term = request.args.get("search", "").strip()

    # Get all students
    students = User.query.filter_by(role="student").all()

    # Get all performances
    performances = StudentPerformance.query.all()

    # Get unique grades and subjects for filters
    grades = db.session.query(Question.grade).distinct().all()
    subjects = db.session.query(Question.subject).distinct().all()

    # Calculate student performance statistics
    student_stats = []
    for student in students:
        student_performances = [p for p in performances if p.student_id == student.id]

        # Apply filters
        if selected_grade != "all":
            student_performances = [
                p for p in student_performances if p.quiz_grade == selected_grade
            ]
        if selected_subject != "all":
            student_performances = [
                p for p in student_performances if p.quiz_subject == selected_subject
            ]

        total_attempts = len(student_performances)

        if student_performances:
            total_score = sum(p.score for p in student_performances)
            total_questions = sum(p.total_questions for p in student_performances)
            avg_performance = (
                (total_score * 100 / total_questions) if total_questions > 0 else 0
            )

            # Find best performance
            best_performance = max(
                student_performances,
                key=lambda p: p.score / p.total_questions
                if p.total_questions > 0
                else 0,
            )
            best_percentage = (
                (best_performance.score / best_performance.total_questions * 100)
                if best_performance.total_questions > 0
                else 0
            )
        else:
            avg_performance = 0
            best_percentage = 0

        # Apply search filter with exact word matching
        if search_term:
            search_lower = search_term.lower()
            username_lower = student.username.lower()
            email_lower = student.email.lower()

            # Check for exact match or word boundary match
            username_match = (
                username_lower == search_lower
                or username_lower.startswith(search_lower + " ")
                or username_lower.endswith(" " + search_lower)
                or " " + search_lower + " " in username_lower
            )
            email_match = (
                email_lower == search_lower
                or email_lower.startswith(search_lower + " ")
                or email_lower.endswith(" " + search_lower)
                or " " + search_lower + " " in email_lower
            )

            if not username_match and not email_match:
                continue

        student_stats.append(
            {
                "student": student,
                "total_attempts": total_attempts,
                "avg_performance": avg_performance,
                "best_percentage": best_percentage,
            }
        )

    return render_template(
        "admin_students.html",
        title="Student Analysis",
        student_stats=student_stats,
        grades=grades,
        subjects=subjects,
        selected_grade=selected_grade,
        selected_subject=selected_subject,
        search_term=search_term,
    )


@app.route("/admin/analytics")
@login_required
def admin_analytics():
    if current_user.role != "admin":
        return redirect(url_for("index"))

    # Get filter parameters
    selected_grade = request.args.get("grade", "all")
    selected_subject = request.args.get("subject", "all")
    selected_quiz = request.args.get("quiz", "all")

    # Get all performances
    performances_query = StudentPerformance.query

    # Apply filters
    if selected_grade != "all":
        performances_query = performances_query.filter_by(quiz_grade=selected_grade)
    if selected_subject != "all":
        performances_query = performances_query.filter_by(quiz_subject=selected_subject)

    # Get quizzes for the selected grade/subject
    from app.models import Grade, Quiz, Subject

    quizzes = []
    if selected_grade != "all" and selected_subject != "all":
        grade_obj = Grade.query.filter_by(name=selected_grade).first()
        subject_obj = (
            Subject.query.filter_by(
                name=selected_subject, grade_id=grade_obj.id if grade_obj else None
            ).first()
            if grade_obj
            else None
        )
        if grade_obj and subject_obj:
            quizzes = Quiz.query.filter_by(
                grade_id=grade_obj.id, subject_id=subject_obj.id
            ).all()
    quiz_choices = [("all", "All Quizzes")] + [(str(q.id), q.title) for q in quizzes]

    if selected_quiz != "all":
        performances_query = performances_query.filter_by(quiz_id=int(selected_quiz))

    performances = performances_query.all()

    # Get unique grades and subjects for filters
    grades = db.session.query(Question.grade).distinct().all()
    subjects = db.session.query(Question.subject).distinct().all()

    # Get performance by subject (apply same filters)
    subject_query = db.session.query(
        StudentPerformance.quiz_subject,
        db.func.avg(
            StudentPerformance.score * 100.0 / StudentPerformance.total_questions
        ).label("avg_score"),
        db.func.count(StudentPerformance.id).label("attempts"),
        db.func.min(
            StudentPerformance.score * 100.0 / StudentPerformance.total_questions
        ).label("min_score"),
        db.func.max(
            StudentPerformance.score * 100.0 / StudentPerformance.total_questions
        ).label("max_score"),
    ).group_by(StudentPerformance.quiz_subject)

    # Apply filters to subject query
    if selected_grade != "all":
        subject_query = subject_query.filter_by(quiz_grade=selected_grade)
    if selected_subject != "all":
        subject_query = subject_query.filter_by(quiz_subject=selected_subject)

    subject_performance = subject_query.order_by(
        db.func.avg(
            StudentPerformance.score * 100.0 / StudentPerformance.total_questions
        ).desc()
    ).all()

    # Get performance by grade (apply same filters)
    grade_query = db.session.query(
        StudentPerformance.quiz_grade,
        db.func.avg(
            StudentPerformance.score * 100.0 / StudentPerformance.total_questions
        ).label("avg_score"),
        db.func.count(StudentPerformance.id).label("attempts"),
        db.func.min(
            StudentPerformance.score * 100.0 / StudentPerformance.total_questions
        ).label("min_score"),
        db.func.max(
            StudentPerformance.score * 100.0 / StudentPerformance.total_questions
        ).label("max_score"),
    ).group_by(StudentPerformance.quiz_grade)

    # Apply filters to grade query
    if selected_grade != "all":
        grade_query = grade_query.filter_by(quiz_grade=selected_grade)
    if selected_subject != "all":
        grade_query = grade_query.filter_by(quiz_subject=selected_subject)

    grade_performance = grade_query.order_by(StudentPerformance.quiz_grade).all()

    # Get recent activity (apply same filters)
    recent_query = StudentPerformance.query.join(
        User, StudentPerformance.student_id == User.id
    )

    # Apply filters to recent activity
    if selected_grade != "all":
        recent_query = recent_query.filter(
            StudentPerformance.quiz_grade == selected_grade
        )
    if selected_subject != "all":
        recent_query = recent_query.filter(
            StudentPerformance.quiz_subject == selected_subject
        )

    recent_attempts = (
        recent_query.order_by(
            StudentPerformance.timestamp.desc()
            if StudentPerformance.timestamp
            else StudentPerformance.id.desc()
        )
        .limit(20)
        .all()
    )

    return render_template(
        "admin_analytics.html",
        title="Grade & Subject Analytics",
        subject_performance=subject_performance,
        grade_performance=grade_performance,
        recent_attempts=recent_attempts,
        grades=grades,
        subjects=subjects,
        quizzes=quiz_choices,
        selected_grade=selected_grade,
        selected_subject=selected_subject,
        selected_quiz=selected_quiz,
    )


@app.route("/admin/upload_questions", methods=["GET", "POST"])
@login_required
def upload_questions():
    if current_user.role != "admin":
        return redirect(url_for("index"))

    message = None
    success_count = 0
    error_rows = []

    if request.method == "POST":
        file = request.files.get("csv_file")
        if not file or not file.filename.endswith(".csv"):
            message = "Please upload a valid CSV file."
        else:
            try:
                stream = TextIOWrapper(file.stream, encoding="utf-8")
                reader = csv.DictReader(stream)
                required_fields = [
                    "grade",
                    "subject",
                    "quiz_title",
                    "question_text",
                    "option_a",
                    "option_b",
                    "option_c",
                    "option_d",
                    "correct_answer",
                    "explanation",
                ]
                from app.models import Grade, Quiz, Subject

                for i, row in enumerate(reader, start=2):
                    if not all(
                        field in row and row[field].strip() for field in required_fields
                    ):
                        error_rows.append(i)
                        continue
                    # Find or create Grade
                    grade_obj = Grade.query.filter_by(name=row["grade"].strip()).first()
                    if not grade_obj:
                        grade_obj = Grade(name=row["grade"].strip())
                        db.session.add(grade_obj)
                        db.session.flush()
                    # Find or create Subject
                    subject_obj = Subject.query.filter_by(
                        name=row["subject"].strip(), grade_id=grade_obj.id
                    ).first()
                    if not subject_obj:
                        subject_obj = Subject(
                            name=row["subject"].strip(), grade_id=grade_obj.id
                        )
                        db.session.add(subject_obj)
                        db.session.flush()
                    # Find or create Quiz
                    quiz_obj = Quiz.query.filter_by(
                        title=row["quiz_title"].strip(),
                        grade_id=grade_obj.id,
                        subject_id=subject_obj.id,
                    ).first()
                    if not quiz_obj:
                        quiz_obj = Quiz(
                            title=row["quiz_title"].strip(),
                            grade_id=grade_obj.id,
                            subject_id=subject_obj.id,
                            created_by=current_user.username,
                        )
                        db.session.add(quiz_obj)
                        db.session.flush()
                    question = Question(
                        grade=row["grade"].strip(),
                        subject=row["subject"].strip(),
                        question_text=row["question_text"].strip(),
                        option_a=row["option_a"].strip(),
                        option_b=row["option_b"].strip(),
                        option_c=row["option_c"].strip(),
                        option_d=row["option_d"].strip(),
                        correct_answer=row["correct_answer"].strip().lower(),
                        explanation=row["explanation"].strip(),
                        author_id=current_user.id,
                        uploaded_by=current_user.username,
                        quiz_id=quiz_obj.id,
                    )
                    db.session.add(question)
                    success_count += 1
                db.session.commit()
                if success_count:
                    message = f"Successfully uploaded {success_count} questions."
                if error_rows:
                    message = (
                        message or ""
                    ) + f" Skipped rows: {', '.join(map(str, error_rows))}."
            except Exception as e:
                message = f"Error processing file: {e}"

    return render_template(
        "admin_upload_questions.html",
        title="Upload Questions (CSV)",
        message=message,
    )
