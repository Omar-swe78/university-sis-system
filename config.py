import os

ALLOWED_COUNTRIES = [
    "Saudi Arabia", "Egypt", "Jordan", "Lebanon", "United Arab Emirates", "Kuwait", "Qatar", "Bahrain", "Oman", "Yemen", "Sudan", "Morocco", "Algeria", "Tunisia", "Palestine"
]

ALLOWED_MAJORS = [
    "Computer Science", "Engineering", "Business Administration", "Medicine", "Pharmacy", "Law", "Education", "Arts", "Sciences", "Information Technology", "Accounting", "Architecture"
]

AVAILABLE_COURSES = [
    {'name': 'Calc II', 'credit_hours': 4, 'section': 'A', 'room': '201', 'time': 'Sun/Mon/Thu 8:00-9:30'},
    {'name': 'Linear Algebra', 'credit_hours': 3, 'section': 'B', 'room': '105', 'time': 'Sun/Wed 10:00-11:30'},
    {'name': 'Physics I', 'credit_hours': 3, 'section': 'C', 'room': '301', 'time': 'Tue 12:00-13:30'},
    {'name': 'Programming I', 'credit_hours': 3, 'section': 'D', 'room': '210', 'time': 'Wed 14:00-15:30'},
    {'name': 'Statistics', 'credit_hours': 2, 'section': 'E', 'room': '120', 'time': 'Thu 10:00-11:30'},
    {'name': 'Data Structures', 'credit_hours': 3, 'section': 'F', 'room': '215', 'time': 'Sun/Tue 9:00-10:30'},
    {'name': 'Database Systems', 'credit_hours': 3, 'section': 'G', 'room': '220', 'time': 'Mon/Wed 11:00-12:30'},
    {'name': 'Web Development', 'credit_hours': 3, 'section': 'H', 'room': '225', 'time': 'Tue/Thu 13:00-14:30'},
    {'name': 'Machine Learning', 'credit_hours': 4, 'section': 'I', 'room': '230', 'time': 'Sun/Wed 15:00-16:30'},
    {'name': 'Computer Networks', 'credit_hours': 3, 'section': 'J', 'room': '235', 'time': 'Mon/Thu 10:00-11:30'},
    {'name': 'Software Engineering', 'credit_hours': 3, 'section': 'K', 'room': '240', 'time': 'Tue/Fri 14:00-15:30'},
    {'name': 'Operating Systems', 'credit_hours': 4, 'section': 'L', 'room': '245', 'time': 'Wed/Fri 9:00-10:30'},
    {'name': 'Artificial Intelligence', 'credit_hours': 4, 'section': 'M', 'room': '250', 'time': 'Sun/Thu 16:00-17:30'},
    {'name': 'Cybersecurity', 'credit_hours': 3, 'section': 'N', 'room': '255', 'time': 'Mon/Fri 13:00-14:30'},
    {'name': 'Mobile App Development', 'credit_hours': 3, 'section': 'O', 'room': '260', 'time': 'Tue/Sat 10:00-11:30'},
    {'name': 'Calculus II', 'credit_hours': 4, 'section': 'P', 'room': '201', 'time': 'Sun/Mon/Thu 8:00-9:30'},
]

# Development mode flag
DEVELOPMENT_MODE = os.environ.get('FLASK_ENV') == 'development' or os.environ.get('DEVELOPMENT_MODE', 'False').lower() == 'true'

# SMTP Configuration (set these in your local .env or hosting environment)
SMTP_EMAIL = os.environ.get('SMTP_EMAIL', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))

# Database Configuration (SQLite)
DATABASE_PATH = 'university_dev.db' 
