from .abstract_role import AbstractRole
from models.notifications import Notification
from enum import Enum
from datetime import datetime

class Role(Enum):
    ADMIN = "Admin"
    TEACHER = "Teacher"
    STUDENT = "Student"
    PARENT = "Parent"

class User(AbstractRole):
    def __init__(self, id: int, full_name: str, email: str, password_hash: str, created_at: datetime, role: Role):
        super().__init__(id, full_name, email, password_hash, created_at)
        self.role = role
        self.notifications: list[dict] = []
    def get_profile(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role.value,
            "created_at": self.created_at.isoformat()
        }

    def update_profile(self, full_name: str = None, email: str = None):
        if full_name:
            self.full_name = full_name
        if email:
            self.email = email

    def add_notification(self, notification: Notification):
        notification_dict = notification.to_dict()
        self.notifications.append(notification_dict)
    
    def view_notifications(self, unread_only: bool = False, priority: str = None):
        notifications = self.notifications
        if unread_only:
            notifications = [n for n in notifications if not n["is_read"]]
        if priority:
            notifications = [n for n in notifications if n["priority"] == priority]
        return notifications
    def delete_notification(self, id: int):
        self.notifications = [n for n in self.notifications if n["id"] != id]
    