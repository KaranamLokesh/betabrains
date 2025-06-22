# Betabrains Quiz Web Application

A modern quiz web application for schools and students, featuring admin and student roles, quiz management, detailed performance tracking, and an AI-powered tutor for personalized learning.

## Features

- **User Roles:**
  - **Admin:** Upload questions (with options, answers, explanations, metadata), manage quizzes.
  - **Student:** Take quizzes by grade/subject, view results, get personalized feedback, and practice with an AI tutor.
- **Quiz Management:**
  - Upload and categorize questions by grade and subject.
  - Take quizzes, see instant feedback, and review explanations.
- **Performance Tracking:**
  - View past quiz attempts with filtering (by subject, grade, date, score).
  - Sort and search attempts, see average and best scores.
- **AI Tutor:**
  - Practice mode and performance review chat powered by OpenAI's API.
  - Context-aware, personalized help for each student.
- **Authentication:**
  - Register/login as admin or student.
  - Role-based dashboards and access control.

## Tech Stack

- **Backend:** Flask, SQLAlchemy, Flask-Login, Flask-Migrate, Flask-WTF
- **Frontend:** Jinja2 templates, Bootstrap (custom CSS/JS)
- **Database:** SQLite (default, easy to switch)
- **AI Integration:** OpenAI API (for tutor/chat)

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/KaranamLokesh/betabrains.git
   cd betabrains
   ```
2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set environment variables:**
   - Create a `.env` file or export variables in your shell:
     - `FLASK_APP=run.py`
     - `FLASK_ENV=development`
     - `SECRET_KEY=your_secret_key`
     - `OPENAI_API_KEY=your_openai_api_key`
5. **Initialize the database:**
   ```bash
   flask db upgrade
   ```
6. **Run the application:**
   ```bash
   flask run
   ```
   The app will be available at [http://localhost:5000](http://localhost:5000)

## Usage Guide

- **Register** as an admin or student.
- **Admins** can upload questions and manage quizzes from the dashboard.
- **Students** can select quizzes by grade/subject, take quizzes, and view detailed results.
- **Performance** page allows filtering, sorting, and searching past attempts.
- **AI Tutor** is available in practice mode and on performance review pages for personalized help.

## Contribution

Contributions are welcome! Please fork the repo and submit a pull request. For major changes, open an issue first to discuss what you'd like to change.

## License

This project is licensed under the MIT License.