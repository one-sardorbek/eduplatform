from datetime import datetime
from enum import Enum
from data.storage import DataStorage as storage
from models.schedule import Schedule
class Priority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Notification:
    def __init__(self, id : int, message: str, recipient_id: int, created_at: datetime, priority: Priority = Priority.MEDIUM, is_read: bool = False): 
        self.id = id
        self.message = message
        self.recipient_id = recipient_id
        self.created_at = created_at.now().isoformat()
        self.priority = priority
        self.is_read = is_read

    def mark_as_read(self):
        self.is_read = True
    
    def send(self,storage):
        storage.add_notification(self)
        user = storage.get_user(self.recipient_id)
        if user:
            user.add_notification(self)
            return True
        return False
    
    
    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "recipient_id": self.recipient_id,
            "created_at": self.created_at,
            "is_read": self.is_read,
            "priority": self.priority.value
        }
    
    def notify_schedule_change(self, schedule: Schedule, storage: storage):
        student_ids = storage.get_students_by_class(schedule.class_id)
        for student_id in student_ids:
            notification = Notification(
                id=len(storage.notifications) + 1,
                message=f"New schedule added for class {schedule.class_id}",
                recipient_id=student_id,
                priority=Priority.MEDIUM
            )
            notification.send(storage)