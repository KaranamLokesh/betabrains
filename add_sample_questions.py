from app import app, db
from app.models import Grade, Question, Subject

with app.app_context():
    # Clear existing data (optional, for clean test)
    # db.session.query(Question).delete()
    # db.session.query(Subject).delete()
    # db.session.query(Grade).delete()
    # db.session.commit()

    # Add Grades
    grade5 = Grade(name="Grade 5", description="Fifth Grade")
    grade6 = Grade(name="Grade 6", description="Sixth Grade")
    db.session.add_all([grade5, grade6])
    db.session.commit()

    # Add Subjects
    math5 = Subject(
        name="Mathematics", grade_id=grade5.id, description="Math for Grade 5"
    )
    sci5 = Subject(
        name="Science", grade_id=grade5.id, description="Science for Grade 5"
    )
    math6 = Subject(
        name="Mathematics", grade_id=grade6.id, description="Math for Grade 6"
    )
    sci6 = Subject(
        name="Science", grade_id=grade6.id, description="Science for Grade 6"
    )
    db.session.add_all([math5, sci5, math6, sci6])
    db.session.commit()

    # Add Questions for Grade 5 Math
    q1 = Question(
        grade="Grade 5",
        subject="Mathematics",
        grade_id=grade5.id,
        subject_id=math5.id,
        question_text="What is 7 + 8?",
        option_a="13",
        option_b="14",
        option_c="15",
        option_d="16",
        correct_answer="c",
        explanation="7 + 8 = 15.",
        author_id=1,  # Make sure an admin user with id=1 exists
    )
    q2 = Question(
        grade="Grade 5",
        subject="Mathematics",
        grade_id=grade5.id,
        subject_id=math5.id,
        question_text="What is the value of 5 x 6?",
        option_a="30",
        option_b="35",
        option_c="25",
        option_d="20",
        correct_answer="a",
        explanation="5 x 6 = 30.",
        author_id=1,
    )
    # Add Questions for Grade 5 Science
    q3 = Question(
        grade="Grade 5",
        subject="Science",
        grade_id=grade5.id,
        subject_id=sci5.id,
        question_text="What do plants need for photosynthesis?",
        option_a="Sunlight, water, and carbon dioxide",
        option_b="Oxygen and sugar",
        option_c="Only water",
        option_d="Only sunlight",
        correct_answer="a",
        explanation="Plants need sunlight, water, and carbon dioxide for photosynthesis.",
        author_id=1,
    )
    # Add Questions for Grade 6 Math
    q4 = Question(
        grade="Grade 6",
        subject="Mathematics",
        grade_id=grade6.id,
        subject_id=math6.id,
        question_text="What is the area of a rectangle with length 8 and width 3?",
        option_a="24",
        option_b="11",
        option_c="22",
        option_d="18",
        correct_answer="a",
        explanation="Area = length x width = 8 x 3 = 24.",
        author_id=1,
    )
    # Add Questions for Grade 6 Science
    q5 = Question(
        grade="Grade 6",
        subject="Science",
        grade_id=grade6.id,
        subject_id=sci6.id,
        question_text="What is the boiling point of water?",
        option_a="50°C",
        option_b="100°C",
        option_c="0°C",
        option_d="150°C",
        correct_answer="b",
        explanation="Water boils at 100°C.",
        author_id=1,
    )
    db.session.add_all([q1, q2, q3, q4, q5])
    db.session.commit()
    print("Sample grades, subjects, and questions added!")
