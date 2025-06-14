from datetime import datetime
from data.storage import DataStorage as storage
class Grade:
    def __init__(self,id: int, student_id: int, subject: str, value: int, date: datetime, teacher_id: int, comments: list = []):
        
        if not isinstance(id, int) or id <= 0:
            raise ValueError("ID must be a positive integer")
        if not isinstance(student_id, int) or student_id <= 0:
            raise ValueError("Student ID must be a positive integer")
        if not isinstance(teacher_id, int) or teacher_id <= 0:
            raise ValueError("Teacher ID must be a positive integer")
        if not subject:
            raise ValueError("Subject cannot be empty")
        if not isinstance(value, int) or value < 1 or value > 5:
            raise ValueError("Grade value must be between 1 and 5")
        
        
        self.id = id
        self.student_id = student_id
        self.subject = subject
        if value <= 5 and value >= 1:
            self.value = value
        self.date = date.isoformat()
        self.teacher_id = teacher_id
        self.comments = comments

    def update_grade(self, new_value: int, comment: str = None) -> bool:
        if new_value <= 5 and new_value >= 1:
            self.value = new_value
            return True
        if comment is not None:
            self.comments.append(comment)
            return True
        return False
    
    def get_grade_info(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "subject": self.subject,
            "value": self.value,
            "date": self.date,
            "teacher_id": self.teacher_id,
            "comments": self.comments
        }
    def grade_history_for_student(self, student_id: int):
        grades= storage.get_grades_by_student(student_id)
        grades = grades.sort(key=lambda x: x.date, reverse=True)
        return [grade.get_grade_info() for grade in grades]
    
    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "subject": self.subject,
            "value": self.value,
            "date": self.date,
            "teacher_id": self.teacher_id,
            "comments": self.comments
        }
      
    