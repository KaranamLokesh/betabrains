from flask import flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from openai import OpenAI

from app import app, db
from app.forms import (
    ChatForm,
    LoginForm,
    PerformanceFilterForm,
    PracticeForm,
    QuestionForm,
    QuizForm,
    RegistrationForm,
)
from app.models import Question, StudentPerformance, User


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

    # Apply search filter
    if search_term:
        query = query.filter(
            db.or_(
                StudentPerformance.id == search_term
                if search_term.isdigit()
                else db.literal(False),
                StudentPerformance.quiz_subject.ilike(f"%{search_term}%"),
                StudentPerformance.quiz_grade.ilike(f"%{search_term}%"),
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
    questions = Question.query.all()
    return render_template(
        "admin_dashboard.html", title="Admin Dashboard", questions=questions
    )


@app.route("/admin/add_question", methods=["GET", "POST"])
@login_required
def add_question():
    if current_user.role != "admin":
        return redirect(url_for("index"))
    form = QuestionForm()
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
    user_answers = session.get("user_answers", {})
    questions = Question.query.filter_by(
        grade=performance.quiz_grade, subject=performance.quiz_subject
    ).all()
    return render_template(
        "results.html",
        title="Quiz Results",
        performance=performance,
        questions=questions,
        user_answers=user_answers,
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
            )

        except Exception as e:
            flash(f"Error: {e}")
            return render_template(
                "chat.html",
                title="Chat with AI Tutor",
                form=form,
                chat_history=chat_history,
                current_question=current_question,
            )

    return render_template(
        "chat.html",
        title="Chat with AI Tutor",
        form=form,
        chat_history=chat_history,
        current_question=current_question,
    )


@app.route("/student/clear_chat")
@login_required
def clear_chat():
    session.pop("chat_history", None)
    flash("Chat history cleared.")
    return redirect(url_for("chat_with_tutor"))
