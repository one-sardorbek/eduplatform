from typing import List, Optional
from core.user import User, Role
from data.storage import DataStorage
from models.schedule import Schedule
from models.assignments import Assignment
from models.grades import Grade
from utils.export import export_data  
from utils.validation import validate_class_id, validate_time_slot, check_schedule_conflict

class Admin(User):
    def __init__(self, id: int, full_name: str, email: str, password_hash: str):
        super().__init__(id, full_name, email, password_hash, Role.ADMIN)

    def add_user(self, user: User, storage: DataStorage) -> bool:
        """Add a new user to the system."""
        if user.id not in storage.users:
            storage.add_user(user)
            return True
        return False

    def remove_user(self, user_id: int, storage: DataStorage) -> bool:
        """Remove a user from the system."""
        if user_id in storage.users:
            storage.remove_user(user_id)
            return True
        return False

    def add_schedule(self, schedule: Schedule, storage: DataStorage) -> bool:
        """Add a new schedule to the system."""
        if schedule.id not in storage.schedules and validate_class_id(schedule.class_id) and validate_time_slot(schedule.time):
            storage.add_schedule(schedule)
            return True
        return False

    def remove_schedule(self, schedule_id: int, storage: DataStorage) -> bool:
        """Remove a schedule from the system."""
        if schedule_id in storage.schedules:
            storage.remove_schedule(schedule_id)
            return True
        return False

    def add_assignment(self, assignment: Assignment, storage: DataStorage) -> bool:
        """Add a new assignment to the system."""
        if assignment.id not in storage.assignments:
            storage.add_assignment(assignment)
            return True
        return False

    def add_grade(self, grade: Grade, storage: DataStorage) -> bool:
        """Add a new grade to the system."""
        if grade.id not in storage.grades:
            storage.add_grade(grade)
            return True
        return False

    def view_all_users(self, storage: DataStorage) -> List[dict]:
        """View all users in the system."""
        return [user.get_profile() for user in storage.users.values()]
    
    def export_data(self, storage: DataStorage, file_type: str = "csv") -> bool:
        """Export system data (e.g., users, schedules) to a file."""
        data = {
            "users": [user.get_profile() for user in storage.users.values()],
            "schedules": [schedule.to_dict() for schedule in storage.schedules.values()],
            "assignments": [assignment.to_dict() for assignment in storage.assignments.values()],
            "grades": [grade.to_dict() for grade in storage.grades.values()]
        }
        return export_data(data, file_type)