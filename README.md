# University SIS System

University SIS System is a Flask-based student information system for managing university students, teachers, courses, schedules, authentication, and administrative reports.

## Features

- Role-based authentication for admins, students, and teachers
- Admin dashboard for managing students, teachers, and courses
- Student dashboard for course registration, profile details, and schedules
- Teacher dashboard for assigned courses, schedules, and course details
- Export tools for student, teacher, and course data
- Email support for password reset workflows
- Sample demo accounts and seed data for testing

## Tech Stack

- Python
- Flask
- Jinja2 templates
- SQL Server via `pyodbc`
- Pandas, OpenPyXL, ReportLab, and python-docx for exports
- HTML, CSS, and Bootstrap-style templates

## Project Structure

```text
.
├── app.py
├── config.py
├── database_fallback.py
├── blueprints/
├── models/
├── templates/
├── utils/
├── requirements.txt
├── DEMO_ACCOUNTS.md
└── EMAIL_SETUP.md
```

## Setup

1. Clone the repository.

```bash
git clone https://github.com/Omar-swe78/university-sis-system.git
cd university-sis-system
```

2. Create and activate a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Create a local environment file.

```bash
copy .env.example .env
```

5. Update `.env` with your local secret key, email settings, and SQL Server settings.

## Environment Variables

```env
SECRET_KEY=change-me
FLASK_ENV=development
DEVELOPMENT_MODE=true

SMTP_EMAIL=your_email@example.com
SMTP_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

SQL_SERVER=localhost\SQLEXPRESS
SQL_DATABASE=university_management
SQL_USERNAME=your_sql_username
SQL_PASSWORD=your_sql_password
SQL_DRIVER=ODBC Driver 17 for SQL Server
```

## Running The App

```bash
python app.py
```

The app runs locally at:

```text
http://localhost:5000
```

## Demo Accounts

See `DEMO_ACCOUNTS.md` for sample login credentials and testing steps.

## Notes

- `.env`, `.venv`, Python cache files, and local database files are ignored by git.
- Do not commit real email passwords, SQL credentials, API keys, or production secrets.
- Configure strong `SECRET_KEY` and database credentials before deploying.
