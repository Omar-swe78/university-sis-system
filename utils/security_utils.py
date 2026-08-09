import hashlib
import secrets
import re
from functools import wraps
from flask import session, redirect, url_for, request, flash, jsonify
from datetime import datetime, timedelta

def hash_password(password):
    """Hash a password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    try:
        salt, password_hash = hashed_password.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except ValueError:
        return False

def generate_secure_token(length=32):
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)

def validate_password_strength(password):
    """Validate password strength"""
    errors = []
    
    if len(password) < 6:
        errors.append("Password must be at least 6 characters long")
    
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r"[0-9]", password):
        errors.append("Password must contain at least one number")
    
    # Check for common weak passwords
    weak_passwords = ['password', '123456', 'qwerty', 'abc123', 'password123']
    if password.lower() in weak_passwords:
        errors.append("Password is too common and weak")
    
    return errors

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid international format
    if len(digits_only) >= 10 and len(digits_only) <= 15:
        return True
    return False

def validate_university_number(university_number):
    """Validate university number format"""
    # Should be exactly 7 digits
    return re.match(r'^\d{7}$', university_number) is not None

def sanitize_input(input_string):
    """Sanitize user input to prevent XSS attacks"""
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', str(input_string))
    return sanitized.strip()

def require_login(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Authentication required'}), 401
            flash('Please sign in to access this page.', 'warning')
            return redirect(url_for('auth.signin'))
        return f(*args, **kwargs)
    return decorated_function

def require_role(required_role):
    """Decorator to require specific user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.is_json:
                    return jsonify({'success': False, 'message': 'Authentication required'}), 401
                flash('Please sign in to access this page.', 'warning')
                return redirect(url_for('auth.signin'))
            
            user_role = session.get('user_role', '')
            if user_role != required_role and user_role != 'admin':
                if request.is_json:
                    return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit_check(user_id, action, max_attempts=5, window_minutes=15):
    """Check if user has exceeded rate limit for specific action"""
    # In a production environment, this would use Redis or similar
    # For now, we'll use session-based rate limiting
    
    rate_limit_key = f"rate_limit_{user_id}_{action}"
    current_time = datetime.now()
    
    if rate_limit_key not in session:
        session[rate_limit_key] = []
    
    # Clean old attempts outside the window
    session[rate_limit_key] = [
        attempt_time for attempt_time in session[rate_limit_key]
        if datetime.fromisoformat(attempt_time) > current_time - timedelta(minutes=window_minutes)
    ]
    
    # Check if limit exceeded
    if len(session[rate_limit_key]) >= max_attempts:
        return False
    
    # Record this attempt
    session[rate_limit_key].append(current_time.isoformat())
    return True

def log_security_event(user_id, event_type, details, ip_address=None):
    """Log security-related events"""
    try:
        # In a production environment, this would log to a security log file or database
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'event_type': event_type,
            'details': details,
            'ip_address': ip_address or request.remote_addr if request else None
        }
        
        # For now, just print to console
        print(f"SECURITY LOG: {log_entry}")
        
        # In production, you would save this to a database or log file
        # execute_query(
        #     "INSERT INTO SecurityLogs (user_id, event_type, details, ip_address, timestamp) VALUES (?, ?, ?, ?, ?)",
        #     [user_id, event_type, details, ip_address, datetime.now()]
        # )
        
    except Exception as e:
        print(f"Error logging security event: {e}")

def validate_csrf_token(token):
    """Validate CSRF token"""
    expected_token = session.get('csrf_token')
    return expected_token and secrets.compare_digest(expected_token, token)

def generate_csrf_token():
    """Generate CSRF token"""
    token = generate_secure_token()
    session['csrf_token'] = token
    return token

def check_password_history(user_id, new_password, history_count=5):
    """Check if password was used recently"""
    try:
        # In production, you would check against a password history table
        # For now, we'll skip this check
        return True
    except Exception:
        return True

def validate_session_security():
    """Validate session security"""
    # Check session timeout
    if 'last_activity' in session:
        last_activity = datetime.fromisoformat(session['last_activity'])
        if datetime.now() - last_activity > timedelta(hours=2):
            session.clear()
            return False
    
    # Update last activity
    session['last_activity'] = datetime.now().isoformat()
    
    # Check for session hijacking (basic check)
    current_user_agent = request.headers.get('User-Agent', '')
    session_user_agent = session.get('user_agent', '')
    
    if session_user_agent and current_user_agent != session_user_agent:
        log_security_event(
            session.get('user_id'),
            'SESSION_HIJACKING_ATTEMPT',
            f'User agent mismatch: {current_user_agent} vs {session_user_agent}'
        )
        session.clear()
        return False
    
    # Store user agent if not already stored
    if not session_user_agent:
        session['user_agent'] = current_user_agent
    
    return True

def secure_headers():
    """Add security headers to response"""
    def add_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https:; font-src 'self' https://cdn.jsdelivr.net;"
        return response
    return add_headers

def validate_file_upload(file, allowed_extensions=None, max_size_mb=5):
    """Validate file upload security"""
    if not file or not file.filename:
        return False, "No file selected"
    
    if allowed_extensions is None:
        allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
    
    # Check file extension
    if '.' not in file.filename:
        return False, "File must have an extension"
    
    extension = file.filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > max_size_mb * 1024 * 1024:
        return False, f"File too large. Maximum size: {max_size_mb}MB"
    
    return True, "File is valid"

def escape_sql_like(value):
    """Escape special characters in SQL LIKE queries"""
    return value.replace('%', '\\%').replace('_', '\\_') if value else value

