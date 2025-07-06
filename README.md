# Betabrains Quiz Web Application

A modern, intelligent quiz web application for schools and students, featuring admin and student roles, comprehensive quiz management, detailed performance tracking, and an AI-powered tutor for personalized learning. Built with a beautiful, responsive Bootstrap 5 interface.

## ✨ Features

### 🎯 **User Roles & Authentication**
- **Admin Dashboard:** Upload questions with options, answers, explanations, and metadata. Manage quizzes with a modern interface.
- **Student Dashboard:** Take quizzes by grade and subject, view results, get personalized feedback, and practice with an AI tutor.
- **Secure Authentication:** Register/login as admin or student with role-based access control.

### 📊 **Quiz Management & Performance**
- **Interactive Quizzes:** Take quizzes with instant feedback, detailed explanations, and progress tracking.
- **Advanced Performance Analytics:** View past attempts with powerful filtering (subject, grade, date, score) and sorting options.
- **Real-time Results:** See detailed breakdowns with correct/incorrect answers and explanations.
- **Performance Insights:** Track average scores, best performances, and improvement trends.

### 🤖 **AI-Powered Learning**
- **Intelligent Tutor:** Practice mode and performance review chat powered by OpenAI's API.
- **Context-Aware Help:** Get personalized assistance for specific questions without spoiling answers.
- **Conversational Learning:** Maintain chat context for continuous learning sessions.
- **Smart Suggestions:** AI provides helpful hints and explanations to improve understanding.

### 🎨 **Modern User Interface**
- **Bootstrap 5 Design:** Clean, responsive, and professional interface.
- **Mobile-First Approach:** Optimized for all devices and screen sizes.
- **Interactive Elements:** Hover effects, smooth transitions, and visual feedback.
- **Intuitive Navigation:** Easy-to-use interface with clear visual hierarchy.
- **Accessibility:** Proper ARIA labels and keyboard navigation support.

## 🛠️ Tech Stack

- **Backend:** Flask, SQLAlchemy, Flask-Login, Flask-Migrate, Flask-WTF
- **Frontend:** Bootstrap 5, Bootstrap Icons, Custom CSS, Jinja2 templates
- **Database:** SQLite (default, easily configurable for production)
- **AI Integration:** OpenAI API (for intelligent tutoring and chat)
- **Styling:** Modern CSS with animations, transitions, and responsive design

## 🚀 Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/KaranamLokesh/betabrains.git
   cd betabrains
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   Create a `.env` file or export variables:
   ```bash
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   # For PostgreSQL, set DATABASE_URL as below:
   # DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/dbname
   ```
   - If `DATABASE_URL` is not set, the app will use SQLite by default.
   - To use PostgreSQL, ensure you have a running PostgreSQL server and set the `DATABASE_URL` accordingly.

5. **Initialize the database:**
   ```bash
   flask db upgrade
   ```

6. **Run the application:**
   ```bash
   flask run
   ```
   The app will be available at [http://localhost:5000](http://localhost:5000)

## 📖 Usage Guide

### **For Students:**
1. **Register/Login** as a student
2. **Select Quizzes** by grade and subject from the dashboard
3. **Take Quizzes** with real-time feedback and explanations
4. **Review Performance** with detailed analytics and filtering
5. **Chat with AI Tutor** for personalized help and practice
6. **Track Progress** with comprehensive performance insights

### **For Administrators:**
1. **Register/Login** as an admin
2. **Add Questions** with multiple choice options and explanations
3. **Manage Content** through the admin dashboard
4. **Monitor Usage** with built-in analytics
5. **Customize Experience** with grade and subject organization

### **Key Features:**
- **Smart Filtering:** Search and filter quiz attempts by ID, subject, grade, or date
- **Performance Analytics:** View average scores, best performances, and trends
- **AI Integration:** Get help on specific questions or general concepts
- **Responsive Design:** Works perfectly on desktop, tablet, and mobile devices

## 🎨 UI/UX Highlights

- **Modern Design:** Clean, professional interface with Bootstrap 5
- **Interactive Elements:** Hover effects, smooth animations, and visual feedback
- **Card-Based Layout:** Organized content with clear visual hierarchy
- **Color-Coded Feedback:** Intuitive scoring and performance indicators
- **Responsive Navigation:** Easy-to-use interface across all devices
- **Professional Styling:** Custom CSS with brand colors and animations

## 🤝 Contribution

Contributions are welcome! Please fork the repo and submit a pull request. For major changes, open an issue first to discuss what you'd like to change.

### **Development Setup:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Bootstrap 5 for the modern UI framework
- OpenAI for AI-powered tutoring capabilities
- Flask community for the excellent web framework
- All contributors and users of this project

---

**Built with ❤️ for better education and learning experiences.**

## ☁️ Deploying to Azure App Service

1. **Provision Azure Resources:**
   - Create an Azure App Service (Linux) and an Azure Database for PostgreSQL.

2. **Configure Environment Variables in Azure:**
   - Set `DATABASE_URL` to your PostgreSQL connection string (e.g., `postgresql+psycopg2://username:password@host:port/dbname`).
   - Set `SECRET_KEY` and `OPENAI_API_KEY` as needed.
   - Set `FLASK_ENV=production`.

3. **Set Startup Command:**
   - Use the following startup command for Azure:
     ```
     gunicorn -w 4 -b 0.0.0.0:8000 app.wsgi:application
     ```

4. **Migrate the Database:**
   - In the Azure Cloud Shell or locally (with the same `DATABASE_URL`), run:
     ```
     flask db upgrade
     ```

5. **Deploy Code:**
   - Push your code to Azure using GitHub Actions, Azure CLI, or FTP as preferred.

6. **Access the App:**
   - Visit your Azure App Service URL to use the deployed app.

## 🧪 Local Testing with PostgreSQL

1. **Install PostgreSQL locally** (if not already installed).
2. **Create a database and user:**
   ```bash
   psql -U postgres
   CREATE DATABASE betabrains_db;
   CREATE USER betabrains_user WITH PASSWORD 'betabrains_pass';
   GRANT ALL PRIVILEGES ON DATABASE betabrains_db TO betabrains_user;
   \q
   ```
3. **Copy `.env.example` to `.env` and update values as needed.**
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Run migrations:**
   ```bash
   flask db upgrade
   ```
6. **Run the app:**
   ```bash
   flask run
   ```