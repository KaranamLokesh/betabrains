from app import app, db
from app.models import Question


def check_questions():
    with app.app_context():
        questions = Question.query.all()
        print(f"Total questions in database: {len(questions)}")

        if questions:
            print("\nAvailable quizzes:")
            quizzes = (
                db.session.query(Question.grade, Question.subject).distinct().all()
            )
            for grade, subject in quizzes:
                count = Question.query.filter_by(grade=grade, subject=subject).count()
                print(f"- Grade {grade}, Subject: {subject} ({count} questions)")
        else:
            print("No questions found in database!")


if __name__ == "__main__":
    check_questions()
