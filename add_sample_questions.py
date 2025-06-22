from app import app, db
from app.models import Question, User


def add_sample_questions():
    with app.app_context():
        # First, let's create an admin user if it doesn't exist
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin", email="admin@example.com", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("Created admin user: admin/admin123")

        # Sample questions for Grade 5 Math
        math_questions = [
            {
                "grade": "5",
                "subject": "Math",
                "question_text": "What is 15 + 27?",
                "option_a": "40",
                "option_b": "42",
                "option_c": "43",
                "option_d": "41",
                "correct_answer": "b",
                "explanation": "15 + 27 = 42. You can solve this by adding the ones place (5+7=12, carry 1) and then the tens place (1+1+2=4).",
            },
            {
                "grade": "5",
                "subject": "Math",
                "question_text": "What is 8 × 6?",
                "option_a": "46",
                "option_b": "48",
                "option_c": "50",
                "option_d": "52",
                "correct_answer": "b",
                "explanation": "8 × 6 = 48. This is a basic multiplication fact that you should memorize.",
            },
            {
                "grade": "5",
                "subject": "Math",
                "question_text": "What is half of 24?",
                "option_a": "10",
                "option_b": "12",
                "option_c": "14",
                "option_d": "16",
                "correct_answer": "b",
                "explanation": "Half of 24 is 12. You can divide 24 by 2 to get 12.",
            },
        ]

        # Sample questions for Grade 5 Science
        science_questions = [
            {
                "grade": "5",
                "subject": "Science",
                "question_text": "What is the largest planet in our solar system?",
                "option_a": "Mars",
                "option_b": "Venus",
                "option_c": "Jupiter",
                "option_d": "Saturn",
                "correct_answer": "c",
                "explanation": "Jupiter is the largest planet in our solar system. It is a gas giant and is much larger than Earth.",
            },
            {
                "grade": "5",
                "subject": "Science",
                "question_text": "What is the process by which plants make their own food?",
                "option_a": "Respiration",
                "option_b": "Photosynthesis",
                "option_c": "Digestion",
                "option_d": "Evaporation",
                "correct_answer": "b",
                "explanation": "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to make their own food (glucose).",
            },
            {
                "grade": "5",
                "subject": "Science",
                "question_text": "What is the hardest natural substance on Earth?",
                "option_a": "Steel",
                "option_b": "Iron",
                "option_c": "Diamond",
                "option_d": "Granite",
                "correct_answer": "c",
                "explanation": "Diamond is the hardest natural substance on Earth. It is made of carbon atoms arranged in a crystal structure.",
            },
        ]

        # Add all questions
        all_questions = math_questions + science_questions

        for q_data in all_questions:
            # Check if question already exists
            existing = Question.query.filter_by(
                question_text=q_data["question_text"]
            ).first()

            if not existing:
                question = Question(
                    grade=q_data["grade"],
                    subject=q_data["subject"],
                    question_text=q_data["question_text"],
                    option_a=q_data["option_a"],
                    option_b=q_data["option_b"],
                    option_c=q_data["option_c"],
                    option_d=q_data["option_d"],
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data["explanation"],
                    author_id=admin.id,
                )
                db.session.add(question)
                print(f"Added question: {q_data['question_text'][:50]}...")
            else:
                print(f"Question already exists: {q_data['question_text'][:50]}...")

        db.session.commit()
        print("\nSample questions added successfully!")
        print("You can now:")
        print("1. Login as admin (admin/admin123) to add more questions")
        print("2. Register as a student to take quizzes")


if __name__ == "__main__":
    add_sample_questions()
