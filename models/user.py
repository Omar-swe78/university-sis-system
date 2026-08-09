import re
import secrets
import hashlib
from utils.security_utils import hash_password, verify_password, validate_password_strength, validate_email, sanitize_input

class User:
    def __init__(self, user_id=None, email=None, password=None, name=None, role=None,
                 verified=False, verify_token=None, reset_token=None, reset_token_expiry=None,
                 nationality=None, gender=None, status=None, major=None):
        self.user_id = user_id
        self.email = email
        self.password = password
        self.name = name
        self.role = role
        self.verified = verified
        self.verify_token = verify_token
        self.reset_token = reset_token
        self.reset_token_expiry = reset_token_expiry
        self.nationality = nationality
        self.gender = gender
        self.status = status
        self.major = major
    
    @classmethod
    def get_all(cls):
        """Get all users from database"""
        from database_fallback import execute_query
        query = "SELECT UserID as user_id, Email as email, Password as password, Name as name, Role as role, Verified as verified, VerifyToken as verify_token, ResetToken as reset_token, ResetTokenExpiry as reset_token_expiry, Nationality as nationality, Gender as gender, Status as status, Major as major FROM Users ORDER BY Name"
        result = execute_query(query, fetch=True)
        if result:
            return [cls(**row) for row in result]
        return []
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID"""
        from database_fallback import execute_query
        query = "SELECT UserID as user_id, Email as email, Password as password, Name as name, Role as role, Verified as verified, VerifyToken as verify_token, ResetToken as reset_token, ResetTokenExpiry as reset_token_expiry, Nationality as nationality, Gender as gender, Status as status, Major as major FROM Users WHERE UserID = ?"
        result = execute_query(query, params=(user_id,), fetchone=True)
        if result:
            return cls(**result)
        return None
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        from database_fallback import execute_query
        query = "SELECT UserID as user_id, Email as email, Password as password, Name as name, Role as role, Verified as verified, VerifyToken as verify_token, ResetToken as reset_token, ResetTokenExpiry as reset_token_expiry, Nationality as nationality, Gender as gender, Status as status, Major as major FROM Users WHERE Email = ?"
        result = execute_query(query, params=(email,), fetchone=True)
        if result:
            return cls(**result)
        return None
    
    @classmethod
    def get_by_verify_token(cls, token):
        """Get user by verification token"""
        from database_fallback import execute_query
        query = "SELECT UserID as user_id, Email as email, Password as password, Name as name, Role as role, Verified as verified, VerifyToken as verify_token, ResetToken as reset_token, ResetTokenExpiry as reset_token_expiry, Nationality as nationality, Gender as gender, Status as status, Major as major FROM Users WHERE VerifyToken = ?"
        result = execute_query(query, params=(token,), fetchone=True)
        if result:
            return cls(**result)
        return None
    
    @classmethod
    def get_by_reset_token(cls, token):
        """Get user by reset token"""
        from database_fallback import execute_query
        query = "SELECT UserID as user_id, Email as email, Password as password, Name as name, Role as role, Verified as verified, VerifyToken as verify_token, ResetToken as reset_token, ResetTokenExpiry as reset_token_expiry, Nationality as nationality, Gender as gender, Status as status, Major as major FROM Users WHERE ResetToken = ?"
        result = execute_query(query, params=(token,), fetchone=True)
        if result:
            return cls(**result)
        return None
    
    def save(self):
        """Save user to database"""
        from database_fallback import execute_query
        if self.user_id:
            # Update existing user
            query = """UPDATE Users 
                      SET Email=?, Password=?, Name=?, Role=?, Verified=?, VerifyToken=?, 
                          ResetToken=?, ResetTokenExpiry=?, Nationality=?, Gender=?, Status=?, Major=?
                      WHERE UserID=?"""
            params = (self.email, self.password, self.name, self.role, self.verified,
                     self.verify_token, self.reset_token, self.reset_token_expiry,
                     self.nationality, self.gender, self.status, self.major, self.user_id)
        else:
            # Create new user
            query = """INSERT INTO Users (Email, Password, Name, Role, Verified, VerifyToken, 
                                        ResetToken, ResetTokenExpiry, Nationality, Gender, Status, Major)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            params = (self.email, self.password, self.name, self.role, self.verified,
                     self.verify_token, self.reset_token, self.reset_token_expiry,
                     self.nationality, self.gender, self.status, self.major)
        
        result = execute_query(query, params=params)
        if result and not self.user_id:
            self.user_id = result
        return result is not None
    
    def delete(self):
        """Delete user from database"""
        from database_fallback import execute_query
        if self.user_id:
            query = "DELETE FROM Users WHERE UserID = ?"
            result = execute_query(query, params=(self.user_id,))
            return result is not None
        return False
    
    def validate(self, exclude_current=False, check_password=True):
        """Validate user data"""
        errors = []
        
        # Validate name
        if not self.name or len(self.name.strip()) < 3:
            errors.append("Name must be at least 3 characters long")
        elif len(self.name) > 100:
            errors.append("Name must be less than 100 characters")
        
        # Validate email
        if not self.email or not validate_email(self.email):
            errors.append("Please enter a valid email address")
        elif len(self.email) > 100:
            errors.append("Email must be less than 100 characters")
        else:
            # Check if email already exists
            existing = User.get_by_email(self.email)
            if existing and (not exclude_current or existing.user_id != self.user_id):
                errors.append("Email address already exists")
        
        # Validate password
        if check_password and self.password:
            password_errors = validate_password_strength(self.password)
            errors.extend(password_errors)
        
        # Validate role
        if not self.role or self.role not in ['student', 'teacher', 'admin']:
            errors.append("Please select a valid role")
        
        # Validate nationality
        if self.nationality and len(self.nationality) > 50:
            errors.append("Nationality must be less than 50 characters")
        
        # Validate gender
        if self.gender and self.gender not in ['Male', 'Female']:
            errors.append("Please select a valid gender")
        
        # Validate status
        if self.status and self.status not in ['Active', 'Inactive', 'Graduated']:
            errors.append("Please select a valid status")
        
        # Validate major
        if self.major and len(self.major) > 50:
            errors.append("Major must be less than 50 characters")
        
        return errors
    
    def check_password(self, password):
        """Check if provided password matches user's password"""
        return verify_password(password, self.password)
    
    def set_password(self, password):
        """Set user's password (hashed)"""
        self.password = hash_password(password)
    
    def generate_verify_token(self):
        """Generate a new verification token"""
        self.verify_token = secrets.token_urlsafe(32)
        return self.verify_token
    
    def generate_reset_token(self):
        """Generate a new password reset token"""
        import datetime
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
        return self.reset_token
    
    def verify_account(self):
        """Mark account as verified"""
        self.verified = True
        self.verify_token = None
        return self.save()
    
    def is_verified(self):
        """Check if account is verified"""
        return bool(self.verified)
    
    def is_reset_token_valid(self):
        """Check if reset token is valid and not expired"""
        if not self.reset_token or not self.reset_token_expiry:
            return False
        import datetime
        return datetime.datetime.now() < self.reset_token_expiry
    
    def clear_reset_token(self):
        """Clear reset token after password reset"""
        self.reset_token = None
        self.reset_token_expiry = None
        return self.save()
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'verified': self.verified,
            'nationality': self.nationality,
            'gender': self.gender,
            'status': self.status,
            'major': self.major
        }
    
    def __repr__(self):
        return f"<User {self.name} ({self.email})>"

