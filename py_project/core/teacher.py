from .user import User
from data.storage import DataStorage as storage
from datetime import datetime
class Teacher(User):
    def __init__(self, id: int, full_name: str, email: str, password_hash: str):
        from .enum import Role
        super().__init__(id, full_name, email, password_hash,role= Role.TEACHER, created_at=datetime.now())
        self.subjects = []  # List of subjects taught by the teacher
        self.classes = []  # List of classes the teacher is assigned to
        self.assignments = {}  # Dictionary to hold assignments created by the teacher

    def create_assignment(self, assignment):
        """Create a new assignment."""
        if assignment.id in self.assignments:
            raise ValueError("Assignment with this ID already exists.")
        self.assignments[assignment.id] = assignment
        storage.add_assignment(assignment)  # Store the assignment in the data storage
        storage.assign_assignment_to_class(assignment.id, assignment.class_id)  # Assign to class

    def grade_assignment(self,assignment_id: int, student_id: int, grade: int):
        """Grade a student's assignment."""
        assignment = storage.get_assignment(assignment_id)
        if not assignment:
            raise ValueError("Assignment not found.")
        if student_id not in assignment.submissions:
            raise ValueError("No submission found for this student.")
        if not (1 <= grade <= 5):
            raise ValueError("Grade must be between 1 and 5.")
        
        assignment.set_grade(student_id, grade)
    
    def view_student_progress(student_id):
        progress = storage.view_student_progress(student_id)
        if not progress:
            raise ValueError("No progress found for this student.")
        
    def view_schedule(self):
        """View the teacher's schedule."""
        schedule = storage.get_schedule_by_teacher(self.id)
        if not schedule:
            return {}
        return {day: lessons for day, lessons in schedule.items() if lessons['teacher_id'] == self.id}