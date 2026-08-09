import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User
from utils.email_utils import send_verification_email, send_password_reset_email
from utils.security_utils import validate_password_strength
from config import ALLOWED_COUNTRIES, ALLOWED_MAJORS, DEVELOPMENT_MODE

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        # Debug print to check password value
        print(f"[DEBUG] Password received: '{password}'")
        role = request.form.get('role', '')
        nationality = request.form.get('nationality', '')
        gender = request.form.get('gender', '')
        status = request.form.get('status', '')
        major = request.form.get('major', '')
        
        # Basic validation
        errors = []
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if not gender:
            errors.append('Please select your gender.')
        
        if not status:
            errors.append('Please select your status.')
        
        # Debug password validation
        print(f"[DEBUG] Password length: {len(password)}")
        print(f"[DEBUG] Password contains lowercase: {bool(re.search(r'[a-z]', password))}")
        print(f"[DEBUG] Password contains uppercase: {bool(re.search(r'[A-Z]', password))}")
        print(f"[DEBUG] Password contains number: {bool(re.search(r'[0-9]', password))}")
        
        # Create user object and validate (without hashing password first)
        user = User(
            email=email,
            password=password,  # Keep original password for validation
            name=name,
            role=role,
            nationality=nationality,
            gender=gender,
            status=status,
            major=major if role == 'teacher' else None
        )
        
        validation_errors = user.validate()
        print(f"[DEBUG] Validation errors: {validation_errors}")
        errors.extend(validation_errors)
        
        # Only hash password if validation passes
        if not errors:
            user.set_password(password)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('signup.html', 
                                 allowed_countries=ALLOWED_COUNTRIES,
                                 allowed_majors=ALLOWED_MAJORS)
        
        # Generate verification token
        user.generate_verify_token()
        
        # Save user to database
        if user.save():
            # If user is a student, create student record
            if role == 'student':
                from models.student import Student
                student = Student(
                    full_name=name,
                    nationality=nationality,
                    status=status,
                    university_number=f"2022{len(str(hash(email))) % 1000:03d}",  # Generate university number
                    email=email,
                    major=major if major else 'Computer Science',
                    gender=gender
                )
                if not student.save():
                    print(f"Warning: Failed to create student record for {email}")
            
            # If user is a teacher, create teacher record
            elif role == 'teacher':
                from models.teacher import Teacher
                teacher = Teacher(
                    teacher_fullname=name,
                    email=email,
                    major=major if major else 'Computer Science',
                    phone=''
                )
                if not teacher.save():
                    print(f"Warning: Failed to create teacher record for {email}")
            
            # Send verification email
            if send_verification_email(user):
                if DEVELOPMENT_MODE:
                    flash('Account created successfully! In development mode, verification emails are logged to console. You can now sign in.', 'success')
                else:
                    flash('Account created! Please check your email to verify your account before signing in.', 'success')
            else:
                if DEVELOPMENT_MODE:
                    flash('Account created successfully! Email verification is disabled in development mode. You can now sign in.', 'warning')
                else:
                    flash('Account created but verification email could not be sent. Please contact support.', 'warning')
            return redirect(url_for('auth.signin'))
        else:
            flash('An error occurred while creating your account. Please try again.', 'error')
    
    return render_template('signup.html', 
                         allowed_countries=ALLOWED_COUNTRIES,
                         allowed_majors=ALLOWED_MAJORS)

@auth_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Basic validation
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('signin.html')
        
        # Find user
        user = User.get_by_email(email)
        if not user:
            flash('Invalid email or password. Please try again.', 'error')
            return render_template('signin.html')
        
        # Check password
        if not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'error')
            return render_template('signin.html')
        
        # Check if account is verified
        if not user.is_verified():
            if DEVELOPMENT_MODE:
                flash('Account not verified, but allowing sign-in in development mode.', 'warning')
            else:
                flash('Please verify your email before signing in. Check your inbox.', 'error')
                return render_template('signin.html')
        
        # Set session
        session['user_id'] = user.user_id
        session['user_email'] = user.email
        session['user_name'] = user.name
        session['user_role'] = user.role
        
        flash('Welcome back! You have successfully signed in.', 'success')
        
        # Redirect based on role
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user.role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    
    return render_template('signin.html')

@auth_bp.route('/verify/<token>')
def verify_email(token):
    user = User.get_by_verify_token(token)
    if user:
        if user.verify_account():
            flash('Your account has been verified! You can now sign in.', 'success')
        else:
            flash('An error occurred while verifying your account. Please try again.', 'error')
    else:
        flash('Invalid or expired verification link.', 'error')
    
    return redirect(url_for('auth.signin'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Please enter your email address.', 'error')
            return render_template('forgot_password.html')
        
        # Find user by email
        user = User.get_by_email(email)
        if user:
            # Generate reset token
            reset_token = user.generate_reset_token()
            user.save()
            
            # Send reset email
            if send_password_reset_email(user, reset_token):
                if DEVELOPMENT_MODE:
                    flash('Password reset email sent! In development mode, check the console for the reset link.', 'success')
                    print(f"[DEV] Password reset link: {request.url_root.rstrip('/')}{url_for('auth.reset_password', token=reset_token)}")
                else:
                    flash('Password reset email sent! Please check your inbox.', 'success')
            else:
                flash('Failed to send password reset email. Please try again.', 'error')
        else:
            # Don't reveal if email exists or not for security
            flash('If an account with that email exists, a password reset link has been sent.', 'success')
        
        return redirect(url_for('auth.signin'))
    
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Get user by reset token
    user = User.get_by_reset_token(token)
    
    if not user or not user.is_reset_token_valid():
        flash('Invalid or expired password reset link.', 'error')
        return redirect(url_for('auth.signin'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate passwords
        if not password or not confirm_password:
            flash('Please enter both password fields.', 'error')
            return render_template('reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)
        
        # Validate password strength
        password_errors = validate_password_strength(password)
        if password_errors:
            for error in password_errors:
                flash(error, 'error')
            return render_template('reset_password.html', token=token)
        
        # Update password
        user.set_password(password)
        user.clear_reset_token()
        
        if user.save():
            flash('Your password has been reset successfully! You can now sign in with your new password.', 'success')
            return redirect(url_for('auth.signin'))
        else:
            flash('An error occurred while resetting your password. Please try again.', 'error')
    
    return render_template('reset_password.html', token=token)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('welcome'))

