from datetime import datetime
from data.storage import DataStorage as storage
from models.grades import Grade
from core.student import Student
from utils.validation import validate_class_id
class Assignment:
    def __init__(self, id: int, title: str, description: str, deadline: datetime, subject: str, teacher_id: int, class_id: str,difficulty: str = "o'rta"):
        
        if not isinstance(id, int) or id <= 0:
            raise ValueError("ID must be a positive integer")
        if not isinstance(teacher_id, int) or teacher_id <= 0:
            raise ValueError("Teacher ID must be a positive integer")
        if not title:
            raise ValueError("Title cannot be empty")
        if not subject:
            raise ValueError("Subject cannot be empty")
        if not class_id or not validate_class_id(class_id):
            raise ValueError("Class ID must be a valid string eg: '9-A'")
        if difficulty not in ["oson", "o'rta", "qiyin"]:
            raise ValueError("Difficulty must be 'oson', 'o'rta', or 'qiyin'")
        

        self.id = id
        self.title = title
        self.description = description
        self.deadline = deadline.isoformat()
        self.subject = subject
        self.teacher_id = teacher_id
        self.class_id = class_id
        self.difficulty = difficulty
        self.submissions = {}
        self.grades = {}

    def add_submission(self, student_id: int, content: str):
        if student_id not in self.submissions:
            self.submissions[student_id] = content
            return True
        return False
    def set_grade(self,student_id: int, grade: int):
        if not isinstance(grade, int) or grade < 1 or grade > 5:
            return False
        if student_id in self.submissions:
            self.grades[student_id] = grade 
            if storage:
                # Create a Grade object and store it
                grade_obj = Grade(
                    id=len(storage.grades) + 1,
                    student_id=student_id,
                    subject=self.subject,
                    value=grade,
                    date=datetime.now(),
                    teacher_id=self.teacher_id
                )
                storage.add_grade(grade_obj)
            student = storage.get_user(student_id)
            if isinstance(student, Student):
                student.grades[self.subject] = grade
                student.assignments[self.id] = self.title
                # Notify the student about the new grade
                notification_message = f"Your assignment '{self.title}' has been graded with {grade}."
                notification = {
                    "message": notification_message,
                    "recipient_id": student_id,
                    "created_at": datetime.now().isoformat(),
                    "priority": "Medium"
                }
                student.add_notification(notification)

            return True   
            return True
        return False
    def get_status(self, student_id: int = None):
        if student_id is None:
            return {
                "total_submissions": len(self.submissions),
                "total_grades": len(self.grades)
            }
        
        if student_id in self.submissions:
            return {
                "submitted": True,
                "grade": self.grades.get(student_id, None)
            }
        return {
            "submitted": False,
            "grade": None
        }
    