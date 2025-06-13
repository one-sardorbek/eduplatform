from datetime import datetime
from typing import Dict, List

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

def check_schedule_conflict(schedule: Dict, new_lesson: Dict) -> bool:
    """Check if adding a new lesson causes a time conflict in the schedule."""
    for lesson in schedule.values():
        if lesson.get("time") == new_lesson.get("time"):
            return True
    return False