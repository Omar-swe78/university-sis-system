# Demo Accounts & Test Data

## Login Credentials

### Admin Account
- **Email**: admin@university.edu
- **Password**: admin123
- **Role**: Administrator
- **Access**: Full system access, student/teacher management, reports, exports

### Student Account
- **Email**: student@university.edu
- **Password**: student123
- **Role**: Student
- **Access**: Course registration, schedule viewing, personal information

### Teacher Account
- **Email**: teacher@university.edu
- **Password**: teacher123
- **Role**: Teacher
- **Access**: Course management, student lists, schedules

## Sample Data Included

### Students (8 sample records)
- Ahmed Ali (Computer Science)
- Fatima Hassan (Engineering)
- Omar Ibrahim (Business Administration)
- Sara Mohammed (Medicine)
- Khalid Al-Rashid (Computer Science)
- Layla Al-Zahra (Information Technology)
- Hassan Al-Mahmoud (Accounting)
- Nora Al-Faisal (Architecture)

### Teachers (6 sample records)
- Dr. Mohammed Al-Saud (Computer Science)
- Dr. Aisha Al-Zahra (Mathematics)
- Dr. Hassan Al-Mahmoud (Engineering)
- Dr. Nora Al-Faisal (Business)
- Dr. Khalid Al-Rashid (Information Technology)
- Dr. Sara Al-Mansouri (Medicine)

### Courses (12 sample courses)
- Calculus II, Linear Algebra, Physics I
- Programming I, Data Structures, Database Systems
- Web Development, Machine Learning
- Computer Networks, Software Engineering
- Operating Systems, Artificial Intelligence

### Additional Data
- Sample homework assignments
- Course enrollments
- Attendance records
- Participation data

## Features Available

### CRUD Operations
- ✅ Create, Read, Update, Delete for Students
- ✅ Create, Read, Update, Delete for Teachers
- ✅ Create, Read, Update, Delete for Courses
- ✅ User management with role-based access

### Export Functionality
- ✅ Export to Excel (.xlsx)
- ✅ Export to PDF
- ✅ Export to Word (.docx)
- Available for Students, Teachers, and Courses data

### Validation
- ✅ Client-side form validation
- ✅ Server-side data validation
- ✅ Email format validation
- ✅ Required field validation

### Security Features
- ✅ User authentication
- ✅ Role-based access control
- ✅ Session management
- ✅ Password protection

### Navigation & UI
- ✅ Responsive design (mobile-friendly)
- ✅ Bootstrap-based interface
- ✅ Intuitive navigation
- ✅ Dashboard for each user role

## Quick Test Steps

1. **Login as Admin**
   - Go to `/auth/signin`
   - Use admin@university.edu / admin123
   - Access admin dashboard
   - Try adding/editing students
   - Test export functionality

2. **Login as Student**
   - Use student@university.edu / student123
   - View course registration
   - Check schedule
   - View personal information

3. **Login as Teacher**
   - Use teacher@university.edu / teacher123
   - View assigned courses
   - Check teaching schedule
   - Access course management

## Database Information
- **Type**: SQLite (university_dev.db)
- **Location**: Project root directory
- **Initialization**: Automatic on first run
- **Reset**: Delete university_dev.db and run init_db.py

