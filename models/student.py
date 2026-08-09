from database_fallback import execute_query, get_db_connection
import re
import pyodbc

class Student:
    def __init__(self, student_id=None, full_name=None, nationality=None, status=None, 
                 university_number=None, email=None, major=None, gender=None, phone=None):
        self.student_id = student_id
        self.full_name = full_name
        self.nationality = nationality
        self.status = status
        self.university_number = university_number
        self.email = email
        self.major = major
        self.gender = gender
        self.phone = phone
    
    @classmethod
    def get_all(cls):
        """Get all students from database"""
        query = """SELECT StudentID as student_id, FullName as full_name, 
                  Nationality as nationality, Status as status, 
                  UniversityNumber as university_number, Email as email, 
                  Major as major, Gender as gender, Phone as phone 
                  FROM Students ORDER BY FullName"""
        result = execute_query(query, fetch=True)
        if result:
            return [cls(**row) for row in result]
        return []
    
    @classmethod
    def get_by_id(cls, student_id):
        """Get student by ID"""
        query = """SELECT StudentID as student_id, FullName as full_name, 
                  Nationality as nationality, Status as status, 
                  UniversityNumber as university_number, Email as email, 
                  Major as major, Gender as gender, Phone as phone 
                  FROM Students WHERE StudentID = ?"""
        result = execute_query(query, params=(student_id,), fetchone=True)
        if result:
            return cls(**result)
        return None
    
    @classmethod
    def get_by_university_number(cls, university_number):
        """Get student by university number"""
        try:
            query = """
                SELECT StudentID, FullName, Nationality, Status, 
                       UniversityNumber, Email, Major, Gender, Phone 
                FROM Students 
                WHERE UniversityNumber = ?
            """
            
            result = execute_query(query, (university_number,), fetchone=True)
            if result:
                return cls(
                    student_id=result['StudentID'],
                    full_name=result['FullName'],
                    nationality=result['Nationality'],
                    status=result['Status'],
                    university_number=result['UniversityNumber'],
                    email=result['Email'],
                    major=result['Major'],
                    gender=result['Gender'],
                    phone=result['Phone']
                )
            return None
        except Exception as e:
            print(f"Error getting student by university number: {e}")
            return None
    
    @classmethod
    def get_by_email(cls, email):
        """Get student by email"""
        try:
            query = """SELECT StudentID, FullName, Nationality, Status, UniversityNumber, 
                             Email, Major, Gender, Phone 
                      FROM Students 
                      WHERE Email = ?"""
            result = execute_query(query, params=(email,), fetchone=True)
            if result:
                return cls(
                    student_id=result['StudentID'],
                    full_name=result['FullName'],
                    nationality=result['Nationality'],
                    status=result['Status'],
                    university_number=result['UniversityNumber'],
                    email=result['Email'],
                    major=result['Major'],
                    gender=result['Gender'],
                    phone=result['Phone']
                )
            return None
        except Exception as e:
            print(f"Error checking email: {e}")
            return None
    
    def validate(self):
        """Validate student data"""
        errors = []
        
        # Validate full name
        if not self.full_name or len(self.full_name.strip()) < 3:
            errors.append("Full name must be at least 3 characters long")
        
        # Validate email
        if not self.email or '@' not in self.email:
            errors.append("Valid email address is required")
        
        # Validate university number
        if not self.university_number or not re.match(r'^\d{7}$', self.university_number):
            errors.append("University number must be exactly 7 digits")
        
        # Validate nationality
        if not self.nationality or self.nationality not in ALLOWED_COUNTRIES:
            errors.append("Valid nationality is required")
        
        # Validate major
        if not self.major or self.major not in ALLOWED_MAJORS:
            errors.append("Valid major is required")
        
        # Validate phone (optional)
        if self.phone and not re.match(r'^\+?[0-9]{10,15}$', self.phone):
            errors.append("Phone number must be 10-15 digits, optionally starting with +")
        
        return errors

    def save(self):
        """Save student to database"""
        try:
            conn = get_db_connection()
            if not conn:
                print("Failed to get database connection")
                return False
                
            cursor = conn.cursor()
                
            try:
                # Check for duplicates
                cursor.execute("""
                    SELECT COUNT(*) FROM Students 
                    WHERE (UniversityNumber = ? OR Email = ?) 
                    AND StudentID != ISNULL(?, -1)
                """, (self.university_number, self.email, self.student_id))
                    
                count = cursor.fetchone()[0]
                if count > 0:
                    print("Duplicate university number or email found")
                    return False

                if self.student_id:
                    # Update existing student
                    cursor.execute("""
                        UPDATE Students 
                        SET FullName = ?, Nationality = ?, Status = ?, 
                            UniversityNumber = ?, Email = ?, Major = ?, 
                            Gender = ?, Phone = ?
                        WHERE StudentID = ?
                    """, (
                        self.full_name, self.nationality, self.status,
                        self.university_number, self.email, self.major,
                        self.gender, self.phone, self.student_id
                    ))
                else:
                    # Insert new student
                    cursor.execute("""
                        INSERT INTO Students (
                            FullName, Nationality, Status, UniversityNumber,
                            Email, Major, Gender, Phone
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        self.full_name, self.nationality, 'Active',
                        self.university_number, self.email, self.major,
                        'Male', self.phone
                    ))
                        
                    # Get the new ID
                    cursor.execute("SELECT SCOPE_IDENTITY() AS ID")
                    row = cursor.fetchone()
                    if row:
                        self.student_id = row[0]
                
                conn.commit()
                return True
                    
            except Exception as e:
                print(f"Database error: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
                    
        except Exception as e:
            print(f"Connection error: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def delete(self):
        """Delete student from database and all related records"""
        if not self.student_id:
            return False
            
        try:
            conn = get_db_connection()
            if not conn:
                print("Failed to get database connection")
                return False
                
            cursor = conn.cursor()
            
            try:
                # Delete related records first (in order of dependencies)
                # 1. Delete participation records
                cursor.execute("DELETE FROM Participation WHERE StudentID = ?", (self.student_id,))
                
                # 2. Delete attendance records
                cursor.execute("DELETE FROM Attendance WHERE StudentID = ?", (self.student_id,))
                
                # 3. Delete homework submissions
                cursor.execute("DELETE FROM HomeworkSubmissions WHERE StudentID = ?", (self.student_id,))
                
                # 4. Delete enrollments
                cursor.execute("DELETE FROM Enrollments WHERE StudentID = ?", (self.student_id,))
                
                # 5. Delete the corresponding user record (if exists)
                cursor.execute("DELETE FROM Users WHERE Email = ?", (self.email,))
                
                # 6. Finally delete the student
                cursor.execute("DELETE FROM Students WHERE StudentID = ?", (self.student_id,))
                
                conn.commit()
                return True
                
            except Exception as e:
                print(f"Error deleting student: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
                
        except Exception as e:
            print(f"Connection error: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def to_dict(self):
        """Convert student to dictionary"""
        return {
            'student_id': self.student_id,
            'full_name': self.full_name,
            'nationality': self.nationality,
            'status': self.status,
            'university_number': self.university_number,
            'email': self.email,
            'major': self.major,
            'gender': self.gender,
            'phone': self.phone
        }
    
    def __repr__(self):
        return f"<Student {self.full_name} ({self.university_number})>"

