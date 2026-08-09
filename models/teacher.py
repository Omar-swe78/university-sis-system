from database_fallback import execute_query
import re
from database_fallback import get_db_connection

class Teacher:
    def __init__(self, teacher_id=None, teacher_fullname=None, email=None, major=None, 
                 phone=None, hire_date=None, department=None):
        self.teacher_id = teacher_id
        self.teacher_fullname = teacher_fullname
        self.email = email
        self.major = major
        self.phone = phone
        self.hire_date = hire_date
        self.department = department
    
    @classmethod
    def get_all(cls):
        """Get all teachers from database"""
        query = """SELECT TeacherID as teacher_id, TeacherFullName as teacher_fullname, 
                  Email as email, Major as major, Phone as phone, 
                  HireDate as hire_date, Department as department 
                  FROM Teachers ORDER BY TeacherFullName"""
        result = execute_query(query, fetch=True)
        if result:
            return [cls(**row) for row in result]
        return []
    
    @classmethod
    def get_by_id(cls, teacher_id):
        """Get teacher by ID"""
        query = """SELECT TeacherID as teacher_id, TeacherFullName as teacher_fullname, 
                  Email as email, Major as major, Phone as phone, 
                  HireDate as hire_date, Department as department 
                  FROM Teachers WHERE TeacherID = ?"""
        result = execute_query(query, params=(teacher_id,), fetchone=True)
        if result:
            return cls(**result)
        return None
    
    @classmethod
    def get_by_email(cls, email):
        """Get teacher by email"""
        try:
            query = """SELECT TeacherID, TeacherFullName, Email, Major, Phone, 
                      HireDate, Department 
                      FROM Teachers WHERE Email = ?"""
            result = execute_query(query, params=(email,), fetchone=True)
            if result:
                return cls(
                    teacher_id=result['TeacherID'],
                    teacher_fullname=result['TeacherFullName'],
                    email=result['Email'],
                    major=result['Major'],
                    phone=result['Phone'],
                    hire_date=result['HireDate'],
                    department=result['Department']
                )
            return None
        except Exception as e:
            print(f"Error getting teacher by email: {e}")
            return None
    
    def save(self):
        """Save teacher to database"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                if self.teacher_id:
                    # Update existing teacher
                    query = """
                        UPDATE Teachers 
                        SET TeacherFullName=?, Email=?, Major=?, Phone=?, Department=?
                        WHERE TeacherID=?
                    """
                    params = (self.teacher_fullname, self.email, self.major, self.phone, 
                             self.department, self.teacher_id)
                    cursor.execute(query, params)
                else:
                    # Create new teacher - using SQL Server's OUTPUT clause
                    query = """
                        INSERT INTO Teachers 
                            (TeacherFullName, Email, Major, Phone, Department)
                        OUTPUT 
                            INSERTED.TeacherID
                        VALUES 
                            (?, ?, ?, ?, ?);
                    """
                    params = (self.teacher_fullname, self.email, self.major, self.phone, self.department)
                    cursor.execute(query, params)
                    
                    # Get the new ID
                    row = cursor.fetchone()
                    if row:
                        self.teacher_id = row[0]
                    else:
                        print("Failed to get new teacher ID")
                        return False
                
                conn.commit()
                
                # Verify the operation was successful
                verify_query = "SELECT COUNT(*) FROM Teachers WHERE TeacherID = ?"
                cursor.execute(verify_query, (self.teacher_id,))
                count = cursor.fetchone()[0]
                
                if count > 0:
                    print(f"Successfully saved teacher with ID: {self.teacher_id}")
                    return True
                else:
                    print("Failed to verify teacher save")
                    return False
                
        except Exception as e:
            print(f"Database error in Teacher.save(): {e}")
            return False
    
    def delete(self):
        """Delete teacher from database"""
        try:
            if not self.teacher_id:
                return False
                
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # First, remove teacher from any courses
                cursor.execute("UPDATE Courses SET TeacherID = NULL WHERE TeacherID = ?", (self.teacher_id,))
                
                # Then delete the teacher
                cursor.execute("DELETE FROM Teachers WHERE TeacherID = ?", (self.teacher_id,))
                conn.commit()
                
                # Verify the deletion was successful
                cursor.execute("SELECT COUNT(*) FROM Teachers WHERE TeacherID = ?", (self.teacher_id,))
                count = cursor.fetchone()[0]
                return count == 0
                
        except Exception as e:
            print(f"Database error in Teacher.delete(): {e}")
            return False
    
    def validate(self):
        """Validate teacher data"""
        errors = []
        
        # Validate full name
        if not self.teacher_fullname or len(self.teacher_fullname.strip()) < 3:
            errors.append("Full name must be at least 3 characters long")
        elif len(self.teacher_fullname) > 100:
            errors.append("Full name must be less than 100 characters")
        
        # Validate email
        if not self.email:
            errors.append("Email is required")
        elif not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', self.email):
            errors.append("Please enter a valid email address")
        elif len(self.email) > 100:
            errors.append("Email must be less than 100 characters")
        else:
            # Check if email already exists
            existing = Teacher.get_by_email(self.email)
            if existing and existing.teacher_id != self.teacher_id:
                errors.append("Email address already exists")
        
        # Validate major
        if not self.major:
            errors.append("Please select a major")
        elif len(self.major) > 50:
            errors.append("Major must be less than 50 characters")
        
        # Validate department
        if self.department and len(self.department) > 50:
            errors.append("Department must be less than 50 characters")
        
        # Validate phone (optional)
        if self.phone:
            # Remove any spaces, dashes, or parentheses
            clean_phone = re.sub(r'[\s\-\(\)]', '', self.phone)
            # Check if it starts with + (optional) followed by 10-15 digits
            if not re.match(r'^\+?\d{10,15}$', clean_phone):
                errors.append("Please enter a valid phone number (10-15 digits, may start with +)")
        
        return errors
    
    def get_courses(self):
        """Get courses taught by this teacher"""
        query = """SELECT CourseID, course_name, course_code, credit_hours, section, room, time_schedule, max_students
                   FROM Courses WHERE teacher_id = ? ORDER BY course_name"""
        result = execute_query(query, params=(self.teacher_id,), fetch=True)
        return result if result else []
    
    def to_dict(self):
        """Convert teacher to dictionary"""
        return {
            'teacher_id': self.teacher_id,
            'teacher_fullname': self.teacher_fullname,
            'email': self.email,
            'major': self.major,
            'phone': self.phone,
            'hire_date': self.hire_date,
            'department': self.department
        }
    
    def __repr__(self):
        return f"<Teacher {self.teacher_fullname} ({self.email})>"

