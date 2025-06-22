from app import app, db
from app.models import User

with app.app_context():
    # Check if admin user already exists
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", email="admin@example.com", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin/admin123")
    else:
        print("Admin user already exists: admin/admin123")

    # Also create a test student
    student = User.query.filter_by(username="student").first()
    if not student:
        student = User(username="student", email="student@example.com", role="student")
        student.set_password("student123")
        db.session.add(student)
        db.session.commit()
        print("Student user created: student/student123")
    else:
        print("Student user already exists: student/student123")
