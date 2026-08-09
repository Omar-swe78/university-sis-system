from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_cors import CORS
import os
from datetime import datetime
 

# Import blueprints
from blueprints.auth import auth_bp

# Import models
from models.student import Student
from models.teacher import Teacher
from models.user import User

# Import utilities
from utils.export_utils import export_students_to_excel, export_students_to_pdf, export_students_to_word, export_courses_to_excel, export_teachers_to_excel
from utils.security_utils import require_login, require_role

# Import configuration
from config import ALLOWED_COUNTRIES, ALLOWED_MAJORS, AVAILABLE_COURSES

# Import database setup (SQLite)
from database_fallback import test_connection, create_database_schema, insert_sample_data, execute_query

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-me-in-development')

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')

# Main routes
@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/dashboard')
@require_login
def dashboard():
    user_role = session.get('user_role', 'student')
    if user_role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif user_role == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))

# Admin routes
@app.route('/admin/dashboard')
@require_login
@require_role('admin')
def admin_dashboard():
    # Get statistics
    students = Student.get_all()
    teachers = Teacher.get_all()
    
    stats = {
        'total_students': len(students),
        'total_teachers': len(teachers),
        'active_students': len([s for s in students if s.status == 'Active']),
        'total_courses': len(AVAILABLE_COURSES)
    }
    
    return render_template('admin_dashboard.html', 
                         admin_name=session.get('user_name', 'Admin'),
                         stats=stats)

@app.route('/teachers')
@require_login
@require_role('admin')
def teachers():
    # Placeholder: In a real app, fetch teachers from the database
    teachers = Teacher.get_all()
    return render_template('teachers.html', teachers=teachers)

@app.route('/courses')
@require_login
@require_role('admin')
def courses():
    courses = execute_query("SELECT * FROM Courses", fetch=True)
    courses = map_courses_list(courses)
    return render_template('courses.html', courses=courses)

@app.route('/courses/add', methods=['GET', 'POST'])
@require_login
@require_role('admin')
def add_course():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip()
        credit_hours = int(request.form.get('credit_hours', 0))
        section = request.form.get('section', '').strip()
        room = request.form.get('room', '').strip()
        time = request.form.get('time', '').strip()
        if not name or not code:
            flash('Course name and code are required.', 'error')
            return render_template('add_course.html')
        # Insert into DB
        execute_query("""
            INSERT INTO Courses (CourseName, CourseCode, CreditHours, Section, Room, TimeSchedule) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, params=(name, code, credit_hours, section, room, time))
        flash('Course added successfully!', 'success')
        return redirect(url_for('courses'))
    return render_template('add_course.html')

@app.route('/courses/edit/<course_code>', methods=['GET', 'POST'])
@require_login
@require_role('admin')
def edit_course(course_code):
    course = execute_query("SELECT * FROM Courses WHERE CourseCode = ?", params=(course_code,), fetchone=True)
    if not course:
        flash('Course not found.', 'error')
        return redirect(url_for('courses'))
    
    course = map_course_keys(course)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip()
        credit_hours = int(request.form.get('credit_hours', 0))
        section = request.form.get('section', '').strip()
        room = request.form.get('room', '').strip()
        time = request.form.get('time', '').strip()
        execute_query("""
            UPDATE Courses 
            SET CourseName=?, CourseCode=?, CreditHours=?, Section=?, Room=?, TimeSchedule=? 
            WHERE CourseCode=?
        """, params=(name, code, credit_hours, section, room, time, course_code))
        flash('Course updated successfully!', 'success')
        return redirect(url_for('courses'))
    return render_template('edit_course.html', course=course)

@app.route('/courses/delete/<course_code>')
@require_login
@require_role('admin')
def delete_course(course_code):
    execute_query("DELETE FROM Courses WHERE CourseCode = ?", params=(course_code,))
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('courses'))

# Student routes
@app.route('/student/dashboard')
@require_login
@require_role('student')
def student_dashboard():
    student_name = session.get('user_name', 'Student')
    student_email = session.get('user_email', '')
    
    # Get registered courses from session (temporary until we implement proper enrollment)
    registered_courses = session.get('registered_courses', [])
    courses = [find_course_by_name(name) for name in registered_courses if find_course_by_name(name)]
    
    # Create weekly schedule
    weekly_schedule = create_weekly_schedule(courses)
    
    # Get current day of the week
    from datetime import datetime
    current_day = datetime.now().strftime('%a')[:3]  # Get abbreviated day name (Sun, Mon, etc.)
    
    # Student info
    student_info = {
        'name': student_name,
        'email': student_email,
        'nationality': 'Saudi Arabia',
        'gender': 'Male',
        'status': 'Active',
        'major': 'Computer Science',
        'university_number': '2022001'
    }
    
    # Available courses
    available_courses = [c for c in AVAILABLE_COURSES if c and c['name'] not in registered_courses]
    
    return render_template('student_dashboard.html',
                         student_name=student_name,
                         student_info=student_info,
                         registered_courses=courses,
                         weekly_schedule=weekly_schedule,
                         current_day=current_day,
                         get_course_room=get_course_room,
                         available_courses=available_courses)

@app.route('/student/info')
@require_login
@require_role('student')
def student_info():
    student_name = session.get('user_name', 'Student')
    student_email = session.get('user_email', '')
    
    student_info = {
        'name': student_name,
        'email': student_email,
        'phone': '+966 555 123 456',
        'nationality': 'Saudi Arabia',
        'gender': 'Male',
        'status': 'Active',
        'standing': 'Good',
        'major': 'Computer Science',
        'university_number': '2022001',
        'cumulative_gpa': 3.75,
        'hours_done': 90,
        'hours_left': 38
    }
    
    return render_template('student_info.html',
                         student_name=student_name,
                         student_info=student_info)

@app.route('/student/courses')
@require_login
@require_role('student')
def student_courses():
    student_name = session.get('user_name', 'Student')
    registered_courses = session.get('registered_courses', [])
    courses = [find_course_by_name(name) for name in registered_courses if find_course_by_name(name)]
    
    # Calculate statistics
    total_credit_hours = sum(course['credit_hours'] for course in courses)
    total_classes = sum(len(course['time'].split('/')) for course in courses)
    
    return render_template('student_courses.html',
                         student_name=student_name,
                         registered_courses=courses,
                         total_credit_hours=total_credit_hours,
                         total_classes=total_classes)

@app.route('/student/schedule')
@require_login
@require_role('student')
def student_schedule():
    student_name = session.get('user_name', 'Student')
    registered_courses = session.get('registered_courses', [])
    courses = [find_course_by_name(name) for name in registered_courses if find_course_by_name(name)]
    weekly_schedule = create_weekly_schedule(courses)
    
    # Calculate statistics
    total_courses = len(courses)
    total_hours = sum(course['credit_hours'] for course in courses)
    
    return render_template('student_schedule.html',
                         student_name=student_name,
                         weekly_schedule=weekly_schedule,
                         total_courses=total_courses,
                         total_hours=total_hours,
                         get_course_room=get_course_room)

@app.route('/student/register-courses', methods=['GET', 'POST'])
@require_login
@require_role('student')
def student_register_courses():
    from models.student import Student
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        action = request.form.get('action', 'register')
        registered_courses = session.get('registered_courses', [])
        # Get student info
        student_email = session.get('user_email')
        student = Student.get_by_email(student_email)
        if course_name and student:
            # Get course_id using correct column names
            course_query = "SELECT CourseID FROM Courses WHERE CourseName = ?"
            course_row = execute_query(course_query, params=(course_name,), fetchone=True)
            if course_row:
                course_id = course_row['CourseID']
                if action == 'register' and course_name not in registered_courses:
                    # Insert into Enrollments if not already enrolled
                    check_query = "SELECT * FROM Enrollments WHERE StudentID = ? AND CourseID = ?"
                    exists = execute_query(check_query, params=(student.student_id, course_id), fetchone=True)
                    if not exists:
                        insert_query = "INSERT INTO Enrollments (StudentID, CourseID) VALUES (?, ?)"
                        execute_query(insert_query, params=(student.student_id, course_id))
                    registered_courses.append(course_name)
                    session['registered_courses'] = registered_courses
                    flash(f'Registered for {course_name} successfully!', 'success')
                elif action == 'drop' and course_name in registered_courses:
                    # Delete from Enrollments
                    delete_query = "DELETE FROM Enrollments WHERE StudentID = ? AND CourseID = ?"
                    execute_query(delete_query, params=(student.student_id, course_id))
                    registered_courses.remove(course_name)
                    session['registered_courses'] = registered_courses
                    flash(f'Dropped {course_name} successfully!', 'success')
        return redirect(url_for('student_register_courses'))
    # Mark registered courses
    registered_courses = session.get('registered_courses', [])
    for course in AVAILABLE_COURSES:
        course['is_registered'] = course['name'] in registered_courses
    # Calculate total credit hours
    registered_course_objects = [find_course_by_name(name) for name in registered_courses if find_course_by_name(name)]
    total_credit_hours = sum(course['credit_hours'] for course in registered_course_objects)
    return render_template('student_register_courses.html',
                         student_name=session.get('user_name', 'Student'),
                         available_courses=AVAILABLE_COURSES,
                         registered_courses=registered_courses,
                         total_credit_hours=total_credit_hours)

# Teacher routes
@app.route('/teacher/dashboard')
@require_login
@require_role('teacher')
def teacher_dashboard():
    from models.teacher import Teacher
    teacher_email = session.get('user_email')
    teacher = Teacher.get_by_email(teacher_email)
    courses = []
    weekly_schedule = []
    if teacher:
        courses_query = "SELECT * FROM Courses WHERE TeacherID = ?"
        courses = execute_query(courses_query, params=(teacher.teacher_id,), fetch=True)
        if courses:
            courses = map_courses_list(courses)
            weekly_schedule = create_weekly_schedule(courses)
        else:
            courses = []  # Ensure courses is a list if query returns None
    else:
        # If no teacher found, try to get courses from config for demo purposes
        courses = AVAILABLE_COURSES[:3]  # Take first 3 courses as demo
        weekly_schedule = create_weekly_schedule(courses)
    # Calculate total students across all courses
    total_students = 0
    if courses:
        for course in courses:
            count_query = "SELECT COUNT(*) as count FROM Enrollments WHERE CourseID = ?"
            count_row = execute_query(count_query, params=(course['CourseID'],), fetchone=True)
            total_students += count_row['count'] if count_row else 0
    
    # Get current day of the week
    from datetime import datetime
    current_day = datetime.now().strftime('%a')[:3]  # Get abbreviated day name (Sun, Mon, etc.)
    
    return render_template('teacher_dashboard.html',
                         teacher_name=teacher.teacher_fullname if teacher else session.get('user_name', 'Teacher'),
                         weekly_schedule=weekly_schedule,
                         courses=courses,
                         total_students=total_students,
                         total_assignments=0,  # Placeholder for assignments
                         current_day=current_day,
                         get_course_room=get_course_room,
                         get_course_section=get_course_section)

@app.route('/teacher/courses')
@require_login
@require_role('teacher')
def teacher_courses():
    from models.teacher import Teacher
    teacher_email = session.get('user_email')
    teacher = Teacher.get_by_email(teacher_email)
    courses = []
    total_hours = 0
    if teacher:
        courses_query = "SELECT * FROM Courses WHERE TeacherID = ?"
        courses = execute_query(courses_query, params=(teacher.teacher_id,), fetch=True)
        if courses:
            courses = map_courses_list(courses)
            total_hours = sum(course['credit_hours'] for course in courses)
            for course in courses:
                count_row = execute_query("SELECT COUNT(*) as count FROM Enrollments WHERE CourseID = ?",
                                          params=(course['CourseID'],), fetchone=True)
                course['student_count'] = count_row['count'] if count_row else 0
        else:
            courses = []  # Ensure courses is a list if query returns None
    # Calculate total students across all courses
    total_students = 0
    if courses:
        for course in courses:
            total_students += course.get('student_count', 0)
    
    return render_template('teacher_courses.html',
                         teacher_name=teacher.teacher_fullname if teacher else session.get('user_name', 'Teacher'),
                         courses=courses,
                         total_hours=total_hours,
                         total_students=total_students)

@app.route('/teacher/course/<course_name>', methods=['GET', 'POST'])
@require_login
@require_role('teacher')
def teacher_course_detail(course_name):
    from urllib.parse import unquote
    course_name = unquote(course_name)
    teacher_name = session.get('user_name', 'Teacher')
    # Find course by name
    course = find_course_by_name(course_name)
    if not course:
        flash('Course not found.', 'error')
        return redirect(url_for('teacher_courses'))
    # Get course_id
    course_id = None
    # Try to get course_id from Courses table using correct column names
    course_query = "SELECT CourseID FROM Courses WHERE CourseName = ?"
    course_row = execute_query(course_query, params=(course_name,), fetchone=True)
    if course_row:
        course_id = course_row['CourseID']
    # Fetch enrolled students and their grades
    students = []
    if course_id:
        enrollments_query = '''
            SELECT s.StudentID, s.FullName, s.UniversityNumber, s.Email, e.Grade
            FROM Enrollments e
            JOIN Students s ON e.StudentID = s.StudentID
            WHERE e.CourseID = ?
        '''
        enrolled = execute_query(enrollments_query, params=(course_id,), fetch=True)
        if enrolled:
            for row in enrolled:
                students.append({
                    'student_id': row['StudentID'],
                    'name': row['FullName'],
                    'university_number': row['UniversityNumber'],
                    'email': row['Email'],
                    'grade': row['Grade'] or ''
                })
    # Handle grade saving
    if request.method == 'POST' and students:
        updated = False
        for student in students:
            field = f"grade_{student['university_number']}"
            grade = request.form.get(field, '').strip()
            # Update grade in Enrollments
            update_query = "UPDATE Enrollments SET grade = ? WHERE student_id = ? AND course_id = ?"
            execute_query(update_query, params=(grade, student['student_id'], course_id))
            student['grade'] = grade
            updated = True
        if updated:
            flash('Grades saved successfully!', 'success')
    return render_template('teacher_course_detail.html',
                         teacher_name=teacher_name,
                         course=course,
                         students=students)

@app.route('/teacher/schedule')
@require_login
@require_role('teacher')
def teacher_schedule():
    teacher_name = session.get('user_name', 'Teacher')
    registered_courses = session.get('registered_courses', [])
    courses = [find_course_by_name(name) for name in registered_courses if find_course_by_name(name)]
    weekly_schedule = create_weekly_schedule(courses)
    
    # Calculate statistics
    total_courses = len(courses)
    total_hours = sum(course['credit_hours'] for course in courses if course and 'credit_hours' in course)
    
    return render_template('teacher_schedule.html',
                         teacher_name=teacher_name,
                         weekly_schedule=weekly_schedule,
                         total_courses=total_courses,
                         total_hours=total_hours,
                         get_course_room=get_course_room)

@app.route('/teacher/register-courses', methods=['GET', 'POST'])
@require_login
@require_role('teacher')
def teacher_register_courses():
    from models.teacher import Teacher
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        action = request.form.get('action', 'register')
        registered_courses = session.get('registered_courses', [])
        # Get teacher info
        teacher_email = session.get('user_email')
        teacher = Teacher.get_by_email(teacher_email)
        if course_name and teacher:
            # Get course_id using correct column names
            course_query = "SELECT CourseID FROM Courses WHERE CourseName = ?"
            course_row = execute_query(course_query, params=(course_name,), fetchone=True)
            if course_row:
                course_id = course_row['CourseID']
                if action == 'register' and course_name not in registered_courses:
                    # Assign teacher to course
                    update_query = "UPDATE Courses SET TeacherID = ? WHERE CourseID = ? AND (TeacherID IS NULL OR TeacherID = ?)"
                    execute_query(update_query, params=(teacher.teacher_id, course_id, teacher.teacher_id))
                    registered_courses.append(course_name)
                    session['registered_courses'] = registered_courses
                    flash(f'Assigned to {course_name} successfully!', 'success')
                elif action == 'drop' and course_name in registered_courses:
                    # Remove teacher from course
                    update_query = "UPDATE Courses SET TeacherID = NULL WHERE CourseID = ? AND TeacherID = ?"
                    execute_query(update_query, params=(course_id, teacher.teacher_id))
                    registered_courses.remove(course_name)
                    session['registered_courses'] = registered_courses
                    flash(f'Removed from {course_name} successfully!', 'success')
        return redirect(url_for('teacher_register_courses'))
    # Mark registered courses and filter available courses
    registered_courses = session.get('registered_courses', [])
    teacher_email = session.get('user_email')
    teacher = Teacher.get_by_email(teacher_email)
    available_courses = []
    for course in AVAILABLE_COURSES:
        # Get course_id and teacher_id from DB using correct column names
        course_row = execute_query("SELECT CourseID, TeacherID FROM Courses WHERE CourseName = ?", params=(course['name'],), fetchone=True)
        if course_row:
            is_registered = (course_row['TeacherID'] == teacher.teacher_id) if teacher else False
            course['is_registered'] = is_registered
            # Only show courses not assigned or assigned to this teacher
            if course_row['TeacherID'] is None or is_registered:
                available_courses.append(course)
    # Calculate total credit hours
    registered_course_objects = [find_course_by_name(name) for name in registered_courses if find_course_by_name(name)]
    total_hours = sum(course['credit_hours'] for course in registered_course_objects if course and 'credit_hours' in course)
    return render_template('teacher_register_courses.html',
                         teacher_name=session.get('user_name', 'Teacher'),
                         available_courses=available_courses,
                         registered_courses=registered_courses,
                         total_hours=total_hours)

# Student management routes
@app.route('/students')
@require_login
@require_role('admin')
def students():
    """Display all students with search and filter functionality"""
    # Get search and filter parameters
    search = request.args.get('search', '').strip()
    major = request.args.get('major', '')
    status = request.args.get('status', '')
    nationality = request.args.get('nationality', '')
    
    # Get all students
    students = Student.get_all()
    
    # Apply filters
    if search:
        students = [s for s in students if search.lower() in s.full_name.lower() or 
                   search.lower() in s.email.lower() or 
                   search.lower() in s.university_number.lower()]
    if major:
        students = [s for s in students if s.major == major]
    if status:
        students = [s for s in students if s.status == status]
    if nationality:
        students = [s for s in students if s.nationality == nationality]
    
    # Calculate statistics
    active_students = len([s for s in students if s.status == 'Active'])
    inactive_students = len([s for s in students if s.status == 'Inactive'])
    
    # Calculate new students this month
    current_month = datetime.now().month
    current_year = datetime.now().year
    new_students_this_month = 0  # This would require a created_at field in the database
    
    return render_template('students.html',
                         students=students,
                         search=search,
                         major=major,
                         status=status,
                         nationality=nationality,
                         active_students=active_students,
                         inactive_students=inactive_students,
                         new_students_this_month=new_students_this_month,
                         allowed_majors=ALLOWED_MAJORS,
                         allowed_countries=ALLOWED_COUNTRIES)

@app.route('/students/add', methods=['GET', 'POST'])
@require_login
@require_role('admin')
def add_student():
    if request.method == 'POST':
        try:
            # Get form data
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip()
            university_number = request.form.get('university_number', '').strip()
            nationality = request.form.get('nationality', '').strip()
            major = request.form.get('major', '').strip()
            gender = request.form.get('gender', 'Male')
            phone = request.form.get('phone', '').strip()
            status = request.form.get('status', 'Active')

            # Basic validation
            if not full_name:
                flash('Full name is required.', 'error')
                return render_template('add_student.html',
                                     allowed_countries=ALLOWED_COUNTRIES,
                                     allowed_majors=ALLOWED_MAJORS)
            
            if not email:
                flash('Email is required.', 'error')
                return render_template('add_student.html',
                                     allowed_countries=ALLOWED_COUNTRIES,
                                     allowed_majors=ALLOWED_MAJORS)
            
            if not university_number:
                flash('University number is required.', 'error')
                return render_template('add_student.html',
                                     allowed_countries=ALLOWED_COUNTRIES,
                                     allowed_majors=ALLOWED_MAJORS)
            
            if not nationality:
                flash('Nationality is required.', 'error')
                return render_template('add_student.html',
                                     allowed_countries=ALLOWED_COUNTRIES,
                                     allowed_majors=ALLOWED_MAJORS)
            
            if not major:
                flash('Major is required.', 'error')
                return render_template('add_student.html',
                                     allowed_countries=ALLOWED_COUNTRIES,
                                     allowed_majors=ALLOWED_MAJORS)

            # Create student object
            student = Student(
                full_name=full_name,
                email=email,
                university_number=university_number,
                nationality=nationality,
                major=major,
                gender=gender,
                phone=phone,
                status=status
            )

            # Save student
            if student.save():
                flash('Student added successfully!', 'success')
                return redirect(url_for('students'))
            else:
                flash('Failed to add student. The university number or email may already be in use.', 'error')
                return render_template('add_student.html',
                                     allowed_countries=ALLOWED_COUNTRIES,
                                     allowed_majors=ALLOWED_MAJORS)

        except Exception as e:
            print(f"Error adding student: {e}")
            flash('An error occurred while adding the student. Please try again.', 'error')
            return render_template('add_student.html',
                                 allowed_countries=ALLOWED_COUNTRIES,
                                 allowed_majors=ALLOWED_MAJORS)

    return render_template('add_student.html',
                         allowed_countries=ALLOWED_COUNTRIES,
                         allowed_majors=ALLOWED_MAJORS)

@app.route('/students/edit/<university_number>', methods=['GET', 'POST'])
@require_login
@require_role('admin')
def edit_student(university_number):
    try:
        # Get student by university number
        student = Student.get_by_university_number(university_number)
        if not student:
            flash('Student not found.', 'error')
            return redirect(url_for('students'))

        if request.method == 'POST':
            # Get form data
            student.full_name = request.form.get('full_name', '').strip()
            student.email = request.form.get('email', '').strip()
            student.nationality = request.form.get('nationality', '').strip()
            student.major = request.form.get('major', '').strip()
            student.gender = request.form.get('gender', 'Male')
            student.phone = request.form.get('phone', '').strip()
            student.status = request.form.get('status', 'Active')

            # Basic validation
            if not student.full_name:
                flash('Full name is required.', 'error')
                return render_template('edit_student.html',
                                     student=student,
                                     allowed_countries=ALLOWED_COUNTRIES,
                                     allowed_majors=ALLOWED_MAJORS)

            if not student.email:
                flash('Email is required.', 'error')
                return render_template('edit_student.html',
                                     student=student,
                                     allowed_countries=ALLOWED_COUNTRIES,
                                     allowed_majors=ALLOWED_MAJORS)

            if not student.nationality:
                flash('Nationality is required.', 'error')
                return render_template('edit_student.html',
                                     student=student,
                                     allowed_countries=ALLOWED_COUNTRIES,
                                     allowed_majors=ALLOWED_MAJORS)

            if not student.major:
                flash('Major is required.', 'error')
                return render_template('edit_student.html',
                                     student=student,
                                     allowed_countries=ALLOWED_COUNTRIES,
                                     allowed_majors=ALLOWED_MAJORS)

            # Save changes
            if student.save():
                flash('Student updated successfully!', 'success')
                return redirect(url_for('students'))
            else:
                flash('Failed to update student. The email may already be in use.', 'error')

        return render_template('edit_student.html',
                             student=student,
                             allowed_countries=ALLOWED_COUNTRIES,
                             allowed_majors=ALLOWED_MAJORS)

    except Exception as e:
        print(f"Error editing student: {e}")
        flash('An error occurred while editing the student.', 'error')
        return redirect(url_for('students'))

@app.route('/students/delete/<university_number>')
@require_login
@require_role('admin')
def delete_student(university_number):
    try:
        student = Student.get_by_university_number(university_number)
        if student:
            if student.delete():
                flash(f'Student "{student.full_name}" deleted successfully!', 'success')
            else:
                flash(f'An error occurred while deleting student "{student.full_name}".', 'error')
        else:
            flash('Student not found.', 'error')
    except Exception as e:
        print(f"Error in delete_student route: {e}")
        flash('An unexpected error occurred while deleting the student.', 'error')
    
    return redirect(url_for('students'))

@app.route('/teachers/add', methods=['GET', 'POST'])
@require_login
@require_role('admin')
def add_teacher():
    if request.method == 'POST':
        # Get form data
        teacher_fullname = request.form.get('teacher_fullname', '').strip()
        email = request.form.get('email', '').strip()
        major = request.form.get('major', '')
        phone = request.form.get('phone', '').strip()
        department = request.form.get('department', '').strip()
        
        # Create teacher object
        teacher = Teacher(
            teacher_fullname=teacher_fullname,
            email=email,
            major=major,
            phone=phone,
            department=department
        )
        
        # Basic validation
        if not teacher_fullname:
            flash('Full name is required.', 'error')
            return render_template('add_teacher.html', 
                                 allowed_majors=ALLOWED_MAJORS,
                                 teacher=teacher)
        
        if not email:
            flash('Email is required.', 'error')
            return render_template('add_teacher.html', 
                                 allowed_majors=ALLOWED_MAJORS,
                                 teacher=teacher)
        
        if not major:
            flash('Major is required.', 'error')
            return render_template('add_teacher.html', 
                                 allowed_majors=ALLOWED_MAJORS,
                                 teacher=teacher)
        
        # Check if email already exists
        existing_teacher = Teacher.get_by_email(email)
        if existing_teacher:
            flash('A teacher with this email already exists.', 'error')
            return render_template('add_teacher.html', 
                                 allowed_majors=ALLOWED_MAJORS,
                                 teacher=teacher)
        
        # Validate teacher data
        errors = teacher.validate()
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('add_teacher.html', 
                                 allowed_majors=ALLOWED_MAJORS,
                                 teacher=teacher)
        
        # Save teacher
        try:
            if teacher.save():
                flash(f'Teacher {teacher.teacher_fullname} has been added successfully!', 'success')
                return redirect(url_for('teachers'))
            else:
                flash('Failed to add teacher. Please try again.', 'error')
                return render_template('add_teacher.html', 
                                     allowed_majors=ALLOWED_MAJORS,
                                     teacher=teacher)
        except Exception as e:
            print(f"Error saving teacher: {e}")
            flash('An error occurred while adding the teacher. Please try again.', 'error')
            return render_template('add_teacher.html', 
                                 allowed_majors=ALLOWED_MAJORS,
                                 teacher=teacher)
    
    return render_template('add_teacher.html', allowed_majors=ALLOWED_MAJORS)

@app.route('/teachers/edit/<int:teacher_id>', methods=['GET', 'POST'])
@require_login
@require_role('admin')
def edit_teacher(teacher_id):
    teacher = Teacher.get_by_id(teacher_id)
    if not teacher:
        flash('Teacher not found.', 'error')
        return redirect(url_for('teachers'))
    
    if request.method == 'POST':
        # Get the original email to check if it changed
        original_email = teacher.email
        
        # Update teacher data
        teacher.teacher_fullname = request.form.get('teacher_fullname', '').strip()
        teacher.email = request.form.get('email', '').strip()
        teacher.major = request.form.get('major', '')
        teacher.phone = request.form.get('phone', '').strip()
        teacher.department = request.form.get('department', '').strip()
        
        # Validate teacher data
        errors = teacher.validate()
        
        # If email changed, check if the new email already exists
        if teacher.email != original_email:
            existing = Teacher.get_by_email(teacher.email)
            if existing and existing.teacher_id != teacher.teacher_id:
                errors.append("Email address already exists")
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('edit_teacher.html',
                                 teacher=teacher,
                                 allowed_majors=ALLOWED_MAJORS)
        
        # Save teacher
        try:
            if teacher.save():
                flash(f'Teacher {teacher.teacher_fullname} has been updated successfully!', 'success')
                return redirect(url_for('teachers'))
            else:
                flash('Failed to update teacher. Please try again.', 'error')
        except Exception as e:
            print(f"Error updating teacher: {e}")
            flash('An error occurred while updating the teacher. Please try again.', 'error')
    
    return render_template('edit_teacher.html',
                         teacher=teacher,
                         allowed_majors=ALLOWED_MAJORS)

@app.route('/teachers/delete/<int:teacher_id>')
@require_login
@require_role('admin')
def delete_teacher(teacher_id):
    teacher = Teacher.get_by_id(teacher_id)
    if not teacher:
        flash('Teacher not found.', 'error')
        return redirect(url_for('teachers'))
    
    try:
        if teacher.delete():
            flash(f'Teacher {teacher.teacher_fullname} has been deleted successfully.', 'success')
        else:
            flash('Failed to delete teacher. Please try again.', 'error')
    except Exception as e:
        print(f"Error deleting teacher: {e}")
        flash('An error occurred while deleting the teacher. Please try again.', 'error')
    
    return redirect(url_for('teachers'))

# Database info route
@app.route('/db-info')
@require_login
def db_info():
    # Test database connection
    success, message = test_connection()
    
    db_info_data = {
        'server': 'SQLite',
        'database': 'university_dev.db',
        'status': 'Connected' if success else 'Connection Failed',
        'connection_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'message': message
    }
    
    if success:
        # Get table information
        students = Student.get_all()
        teachers = Teacher.get_all()
        db_info_data['students_count'] = len(students)
        db_info_data['teachers_count'] = len(teachers)
        db_info_data['tables'] = [
            'Students', 'Teachers', 'Users', 'Courses', 
            'Enrollments', 'Homework', 'HomeworkSubmissions', 
            'Attendance', 'Participation'
        ]
    
    return render_template('db_info.html', db_info=db_info_data)

# Export routes
@app.route('/export/students/<format>')
@require_login
@require_role('admin')
def export_students(format):
    """Export students data in specified format"""
    # Get all students
    students = Student.get_all()
    students_data = []
    
    for student in students:
        students_data.append({
            'ID': student.student_id,
            'Full Name': student.full_name,
            'University Number': student.university_number,
            'Email': student.email,
            'Major': student.major,
            'Nationality': student.nationality,
            'Gender': student.gender,
            'Phone': student.phone,
            'Status': student.status
        })
    
    if format.lower() == 'excel':
        data = export_students_to_excel(students_data)
        if data:
            response = app.response_class(
                data,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={'Content-Disposition': 'attachment; filename=students.xlsx'}
            )
            return response
    elif format.lower() == 'pdf':
        data = export_students_to_pdf(students_data)
        if data:
            response = app.response_class(
                data,
                mimetype='application/pdf',
                headers={'Content-Disposition': 'attachment; filename=students.pdf'}
            )
            return response
    elif format.lower() == 'word':
        data = export_students_to_word(students_data)
        if data:
            response = app.response_class(
                data,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                headers={'Content-Disposition': 'attachment; filename=students.docx'}
            )
            return response
    
    flash('Export failed. Please try again.', 'error')
    return redirect(url_for('students'))

@app.route('/export/teachers/<format>')
@require_login
@require_role('admin')
def export_teachers(format):
    """Export teachers data in specified format"""
    # Get all teachers
    teachers = Teacher.get_all()
    teachers_data = []
    
    for teacher in teachers:
        teachers_data.append({
            'ID': teacher.teacher_id,
            'Full Name': teacher.teacher_fullname,
            'Email': teacher.email,
            'Major': teacher.major,
            'Phone': teacher.phone,
            'Department': teacher.department,
            'Hire Date': teacher.hire_date
        })
    
    if format.lower() == 'excel':
        data = export_teachers_to_excel(teachers_data)
        if data:
            response = app.response_class(
                data,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={'Content-Disposition': 'attachment; filename=teachers.xlsx'}
            )
            return response
    
    flash('Export failed. Please try again.', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/export/courses/<format>')
@require_login
@require_role('admin')
def export_courses(format):
    """Export courses data in specified format"""
    courses_data = []
    for course in AVAILABLE_COURSES:
        courses_data.append({
            'Course Name': course['name'],
            'Credit Hours': course['credit_hours'],
            'Section': course['section'],
            'Room': course['room'],
            'Time': course['time']
        })
    
    if format.lower() == 'excel':
        data = export_courses_to_excel(courses_data)
        if data:
            response = app.response_class(
                data,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={'Content-Disposition': 'attachment; filename=courses.xlsx'}
            )
            return response
    
    flash('Export failed. Please try again.', 'error')
    return redirect(url_for('admin_dashboard'))

# Helper functions
def find_course_by_name(course_name):
    """Find course by name in AVAILABLE_COURSES"""
    return next((c for c in AVAILABLE_COURSES if c['name'] == course_name), None)

def has_time_conflict(new_time, existing_courses):
    """Check if new course time conflicts with existing courses"""
    try:
        parts = new_time.split(' ')
        if len(parts) != 2:
            return False
        
        days_str, time_range = parts
        new_days = days_str.split('/')
        start_time, end_time = time_range.split('-')
        
        def time_to_minutes(t):
            return int(t.split(':')[0]) * 60 + int(t.split(':')[1]) if ':' in t else 0
        
        new_start, new_end = time_to_minutes(start_time), time_to_minutes(end_time)
        
        for course in existing_courses:
            if not course:
                continue
            
            course_parts = course['time'].split(' ')
            if len(course_parts) != 2:
                continue
            
            existing_days_str, existing_time_range = course_parts
            existing_days = existing_days_str.split('/')
            existing_start_time, existing_end_time = existing_time_range.split('-')
            existing_start, existing_end = time_to_minutes(existing_start_time), time_to_minutes(existing_end_time)
            
            # Check for day and time overlap
            for new_day in new_days:
                for existing_day in existing_days:
                    if new_day == existing_day:
                        # Check time overlap
                        if not (new_end <= existing_start or new_start >= existing_end):
                            return True
        
        return False
    except:
        return False

def create_weekly_schedule(courses):
    """Create weekly schedule from courses"""
    schedule = []
    for course in courses:
        if not course:
            continue
        
        try:
            time_parts = course['time'].split(' ')
            if len(time_parts) != 2:
                continue
            
            days_str, time_range = time_parts
            start_time, end_time = time_range.split('-')
            
            for day in days_str.split('/'):
                schedule.append((day, f"{start_time}-{end_time}", course['name']))
        except:
            continue
    
    return schedule

def map_course_keys(course):
    """Normalize DB course row keys to template-friendly keys in-place."""
    if course and 'CourseName' in course:
        course['name'] = course.get('CourseName')
        course['code'] = course.get('CourseCode')
        course['credit_hours'] = course.get('CreditHours')
        course['section'] = course.get('Section')
        course['room'] = course.get('Room')
        course['time'] = course.get('TimeSchedule')
    return course

def map_courses_list(courses):
    """Apply map_course_keys across a list of course rows."""
    if not courses:
        return []
    for c in courses:
        map_course_keys(c)
    return courses

def get_course_room(course_name):
    """Get course room from either config or database"""
    # First try to find in config
    course = find_course_by_name(course_name)
    if course and 'room' in course:
        return course['room']
    
    # If not found in config, try to find in database
    query = "SELECT Room FROM Courses WHERE CourseName = ?"
    result = execute_query(query, params=(course_name,), fetchone=True)
    return result['Room'] if result and 'Room' in result else ''

def get_course_section(course_name):
    """Get course section from either config or database"""
    # First try to find in config
    course = find_course_by_name(course_name)
    if course and 'section' in course:
        return course['section']
    
    # If not found in config, try to find in database
    query = "SELECT Section FROM Courses WHERE CourseName = ?"
    result = execute_query(query, params=(course_name,), fetchone=True)
    return result['Section'] if result and 'Section' in result else ''

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize database on startup
    print("Initializing database...")
    success, message = test_connection()
    if success:
        print("Database connection successful")
        create_database_schema()
        insert_sample_data()
    else:
        print(f"Database connection failed: {message}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
