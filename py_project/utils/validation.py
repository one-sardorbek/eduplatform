from datetime import datetime
from typing import Dict, List
from data.storage import DataStorage as storage
def validate_class_id(class_id: str) -> bool:
    """Validate that class_id follows the format 'number-letter' (e.g., '9-A')."""
    import re
    return bool(re.match(r"^\d+[A-Za-z]$", class_id))

def validate_time_slot(time_str: str) -> bool:
    """Validate that time slot is in 'HH:MM-HH:MM' format (e.g., '09:00-09:45')."""
    try:
        start, end = time_str.split("-")
        datetime.strptime(start, "%H:%M")
        datetime.strptime(end, "%H:%M")
        return True
    except ValueError:
        return False

def check_schedule_conflict(schedule: Dict, new_time: str, class_id: str, day: str, teacher_id: int, storage=storage()) -> bool:
    """Check if adding a new lesson causes a time or teacher conflict in the schedule.
    
    Args:
        schedule (Dict): The current schedule's lessons dictionary {time: {subject, teacher_id}}
        new_time (str): The time slot of the new lesson
        class_id (str): The class ID of the schedule
        day (str): The day of the schedule
        teacher_id (int): The teacher ID of the new lesson
        storage (DataStorage): The data storage instance
    
    Returns:
        bool: True if there’s a conflict, False otherwise
    """
    # Check for time conflict within the current schedule
    if new_time in schedule:
        return True

    # Check for teacher conflict across all schedules
    teacher_lessons = storage.get_schedules_by_teacher(teacher_id)
    for lesson_schedule in teacher_lessons:
        if lesson_schedule.day == day and new_time in lesson_schedule.lessons:
            return True

    # Check for class conflict across all schedules for the same class
    class_lessons = storage.get_schedules_by_class(class_id)
    for lesson_schedule in class_lessons:
        if lesson_schedule.day == day and new_time in lesson_schedule.lessons:
            return True

    return False