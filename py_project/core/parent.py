from .user import User
from data.storage import DataStorage as storage
from models.notifications import Notification, Priority
from datetime import datetime
from models.assignments import Assignment
from typing import List
from .student import Student
class Parent(User):

    def __init__(self, id: int, full_name: str, email: str, password_hash: str,storage= storage()):
        from .enum import Role
        super().__init__(id, full_name, email, password_hash,role= Role.PARENT, created_at=datetime.now())
        self.children = []  # List of child student IDs
    def add_child(self, child_id: int,storage: storage):
        """Add a child to the parent's list of children."""
        if child_id in self.children:
            raise ValueError("Child already added.")
        self.children.append(child_id)
        storage.add_parent_child(self.id, child_id)
    def remove_child(self, child_id: int):
        """Remove a child from the parent's list of children."""
        if child_id not in self.children:
            raise ValueError("Child not found.")
        self.children.remove(child_id)
        storage.remove_parent_child(self.id, child_id)
    def view_children(self):
        """View the list of children associated with this parent."""
        if not self.children:
            raise ValueError("No children found for this parent.")
        return self.children
    
    def view_child_progress(self, child_id: int = None): 
        if child_id is None:
            for child_id in self.children:
                progress = self.storage.view_student_progress(child_id)
                if progress:
                    print(f"Progress for child {child_id}: {progress}")
        else:
            if child_id not in self.children:
                raise ValueError("Child not found.")
            progress = self.storage.view_student_progress(child_id)
            if not progress:
                raise ValueError("No progress found for this child.")
            return progress
        
    def view_child_grades(self, child_id: int= None):
        if child_id is None:
            for child_id in self.children:
                grades = self.storage.get_student_grades(child_id)
                if grades:
                    print(f"Grades for child {child_id}: {grades}")
        else:
            if child_id not in self.children:
                raise ValueError("Child not found.")
            grades = self.storage.get_student_grades(child_id)
            if not grades:
                raise ValueError("No grades found for this child.")
            return grades
        
    def view_child_assignments(self, child_id: int= None):
        if child_id is None:
            for child_id in self.children:
                assignments = self.storage.get_student_assignments(child_id)
                if assignments:
                    print(f"Assignments for child {child_id}: {assignments}")
        else:
            if child_id not in self.children:
                raise ValueError("Child not found.")
            return storage.get_student_assignments(child_id)
    


    def receive_child_notification(self, child_id: int, storage: storage, generate_new: bool = False) -> List[dict]:
        if child_id not in self.children:
            return [{"error": f"Child ID {child_id} is not linked to this parent"}]

        notifications = storage.get_notifications_by_user(self.id)
        if notifications:
            child_notifications = [notif.to_dict() for notif in notifications if f"Child {child_id}" in notif.message]
        else:
            child_notifications = []
        if generate_new:
            grades = storage.get_grades_by_student(child_id)
            for grade in grades:
                if grade.value <= 3 and not any(f"Low grade ({grade.value}) in {grade.subject}" in notif["message"] for notif in child_notifications):
                    new_notification = Notification(
                        id=len(storage.notifications) + 1,
                        message=f"Child {child_id}: Low grade ({grade.value}) in {grade.subject}",
                        recipient_id=self.id,
                        priority=Priority.HIGH
                    )
                    new_notification.send(storage)
                    child_notifications.append(new_notification.to_dict())

            assignments = storage.get_assignments_by_student(child_id)
            student = storage.get_user(child_id)
            if student and isinstance(student, Student):
                for assignment in assignments:
                    assignment_status = student.assignments.get(assignment.id, {})
                    if (datetime.fromisoformat(assignment.deadline) < datetime.now() and
                        (not isinstance(assignment_status, dict) or assignment_status.get("status") != "Submitted") and
                        not any(f"Missed deadline for {assignment.title}" in notif["message"] for notif in child_notifications)):
                        new_notification = Notification(
                            id=len(storage.notifications) + 1,
                            message=f"Child {child_id}: Missed deadline for {assignment.title} in {assignment.subject}",
                            recipient_id=self.id,
                            priority=Priority.MEDIUM
                            
                        )
                        new_notification.send(storage)
                        child_notifications.append(new_notification.to_dict())

        return child_notifications