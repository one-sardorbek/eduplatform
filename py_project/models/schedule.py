from datetime import datetime
from data.storage import DataStorage as storage
from utils.validation import validate_class_id, validate_time_slot, check_schedule_conflict
class Schedule:
    def __init__(self, id: int, class_id: str, day: str):
        self.id = id
        self.class_id = class_id
        self.day = day
        self.lessons = {} # (lug‘at: {time: {subject, teacher_id}})

    def add_lesson(self, time: str, subject: str, teacher_id: int, storage = storage()):
        """Add a lesson to the schedule with conflict checking."""
        if check_schedule_conflict(self.lessons, time, self.class_id, self.day, teacher_id, storage):
            raise ValueError(f"Conflict: Teacher {teacher_id} or class {self.class_id} already has a lesson at {time} on {self.day}")
        if time not in self.lessons:
            self.lessons[time] = {}
            self.lessons[time]['subject'] = subject
            self.lessons[time]['teacher_id'] = teacher_id

    def remove_lesson(self, time: str):
        if time in self.lessons:
            del self.lessons[time]
    
    def view_schedule(self):
        schedule = {
            'id': self.id,
            'class_id': self.class_id,
            'day': self.day,
            'lessons': self.lessons
        }
        return schedule
    