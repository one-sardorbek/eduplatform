from .user import User
from data.storage import DataStorage as storage
from utils.validation import validate_class_id
from datetime import datetime
from typing import Dict
class Student(User):
    def __init__(self, id: int, full_name: str, email: str, password_hash: str, class_id: str):
        from .enum import Role
        super().__init__(id, full_name, email, password_hash,role= Role.STUDENT,created_at=datetime.now()) 
        if validate_class_id(class_id):
            raise ValueError("Class ID must be a valid string eg: '9-A'")
        self.class_id = class_id
        self.subjects = {} 
        self.assignments: Dict[int, Dict[str, str]] = {}
        self.grades = {}

    def submit_assignment(self, assignment_id: int, content: str, storage: storage) -> bool:
        """Submit an assignment with the given content."""
        
        assignment = storage.get_assignment(assignment_id)
        if not assignment:
            raise ValueError(f"Assignment with ID {assignment_id} not found.")
        if assignment.class_id != self.class_id:
            raise ValueError(f"Assignment class {assignment.class_id} does not match student grade {self.class_id}")
        assignment.add_submission(self.id, content)
        self.assignments[assignment_id] = {"status": "Submitted", "content": content}
        # Persist to storage
        storage.update_user_assignments(self.id, self.assignments)
        return True
    
    def view_grades(self, subject: str = None):
        if subject:
            return {k: v for k, v in self.grades.items() if v.subject == subject}
        return self.grades
    def calculate_average_grade(self):
        if not self.grades:
            return 0
        total = sum(grade.value for grade in self.grades.values())
        return total / len(self.grades)
    
    
    def view_schedule(self):
        schedule = storage.get_schedule_by_class(self.class_id)
        if not schedule:
            return {}
        return {day: lessons for day, lessons in schedule.items() if lessons['class_id'] == self.class_id}
    