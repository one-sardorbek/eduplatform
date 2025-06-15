from typing import List, Dict, Optional
from datetime import datetime,timedelta


class DataStorage:
    def __init__(self):
        self.users = {}
        self.assignments = {}
        self.grades = {}
        self.schedules = {}
        self.notifications = {}

    #user management
    def add_user(self, user):
        from core.user import User
        if isinstance(user, User):
            self.users[user.id] = user
    
    def get_user(self, user_id: int):
        return self.users.get(user_id)
    
    def remove_user(self, user_id):
        if user_id in self.users:
            del self.users[user_id]

    def get_students_by_class(self, class_id: str):
        from core.student import Student
        """Retrieve a list of student IDs for a given class."""
        return [user.id for user in self.users.values() if isinstance(user, Student) and user.grades == class_id]        
    
    # Notification management

    def add_notification(self, notification):
        from models.notifications import Notification
        from models.notifications import Priority
        if isinstance(notification, Notification):
            self.notifications[notification.id] = notification
    
    def get_notification(self, notification_id: int):
        return self.notifications.get(notification_id)
    
    def remove_notification(self, notification_id: int):
        if notification_id in self.notifications:
            del self.notifications[notification_id]
    
    def get_notifications_by_user(self, user_id: int, unread_only: bool = False, priority = None):
        from models.notifications import Notification, Priority
        if isinstance(priority, Priority):
            notifications = [n for n in self.notifications.values() if n.recipient_id == user_id]
            if unread_only:
                notifications = [n for n in notifications if not n.is_read]
            if priority:
                notifications = [n for n in notifications if n.priority == priority]
            return notifications
    
    def filter_notifications(self, unread_only: bool = False, priority = None):
        """Filter notifications based on read status and priority."""
        from models.notifications import Notification, Priority
        if isinstance(priority, Priority):
            notifications = list(self.notifications.values())
            if unread_only:
                notifications = [n for n in notifications if not n.is_read]
            if priority:
                notifications = [n for n in notifications if n.priority == priority]
            return notifications
    
    def send_automatic_notification(self, recipient_id: int, priority):
        from models.notifications import Notification, Priority
        if not priority:
            priority = Priority.HIGH
        from core.student import Student
        if isinstance(self.get_user(recipient_id),Student):
            for assignment in self.assignments.values():
                deadline = datetime.fromisoformat(assignment.deadline)
                if assignment.deadline and deadline + timedelta(days =1) == datetime.now():
                    notification = Notification(
                        id=len(self.notifications) + 1,
                        message= f"Reminder: Assignment '{assignment.title}' is due tomorrow.",
                        recipient_id=recipient_id,
                        created_at=datetime.now(),
                        priority=priority
                    )
                    notification.send(self)
                    return True
    
    
    # Schedule Management
    def add_schedule(self, schedule):
        """Add a schedule to the storage."""
        from models.schedule import Schedule
        from models.notifications import Notification
        if isinstance(schedule, Schedule):
            self.schedules[schedule.id] = schedule
        Notification.notify_schedule_change(schedule, self)

    def get_schedule(self, schedule_id: int):
        """Retrieve a schedule by its ID."""
        return self.schedules.get(schedule_id)

    def remove_schedule(self, schedule_id: int):
        """Remove a schedule by its ID."""
        if schedule_id in self.schedules:
            del self.schedules[schedule_id]

    def get_schedules_by_class(self, class_id: str):
        """Retrieve all schedules for a specific class."""
        return [schedule for schedule in self.schedules.values() if schedule.class_id == class_id]

    def get_schedules_by_teacher(self, teacher_id: int):
        """Retrieve all schedules for a specific teacher."""
        return [schedule for schedule in self.schedules.values() if any(lesson["teacher_id"] == teacher_id for lesson in schedule.lessons.values())]
    def get_schedules_by_week(self, week_start: datetime, week_end: datetime):
        """Retrieve all schedules that fall within a specific week."""
        return [schedule for schedule in self.schedules.values() if any(
            datetime.fromisoformat(lesson["time"]) >= week_start and datetime.fromisoformat(lesson["time"]) <= week_end
            for lesson in schedule.lessons.values()
        )]
    
    def get_schedules_by_month(self, month: int, year: int):
        """Retrieve all schedules that fall within a specific month."""
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
        return [schedule for schedule in self.schedules.values() if any(
            start_date <= datetime.fromisoformat(lesson["time"]) < end_date
            for lesson in schedule.lessons.values()
        )]
    
    # Assignment management

    def add_assignment(self, assignment):
        from models.assignments import Assignment
        if isinstance(assignment, Assignment):
            self.assignments[assignment.id] = assignment
        

    def get_assignment(self, assignment_id: int) :
        return self.assignments.get(assignment_id)
    
    def remove_assignment(self, assignment_id: int):
        """Remove an assignment by its ID."""
        if assignment_id in self.assignments:
            del self.assignments[assignment_id]

    def get_assignments_by_class(self, class_id: str):
        """Retrieve all assignments for a specific class."""
        return [assignment for assignment in self.assignments.values() if assignment.class_id == class_id]

    def get_assignments_by_student(self, student_id: int):
        """Retrieve all assignments assigned to a specific student."""
        from core.student import Student
        student = self.get_user(student_id)
        if isinstance(student, Student):
            return [self.assignments[assignment_id] for assignment_id in student.assignments.keys() if assignment_id in self.assignments]
        return []
    
    def assign_assignment_to_class(self, assignment_id: int, class_id: str) -> bool:
        """Assign an assignment to all students in a class."""
        from core.student import Student
        if assignment_id not in self.assignments:
            return False
        student_ids = self.get_students_by_class(class_id)
        for student_id in student_ids:
            student = self.get_user(student_id)
            if isinstance(student, Student):
                student.assignments[assignment_id] = {"status": "Pending", "content": ""}
        return True
    def update_user_assignments(self, user_id: int, assignments: Dict[int, Dict[str, str]]) -> bool:
        from core.student import Student
        """Update the assignments dictionary for a user in storage."""
        user = self.get_user(user_id)
        if isinstance(user, Student):
            user.assignments = assignments
            return True
        return False

    # Grade management

    def add_grade(self, grade):
        """Add a grade to the storage."""
        from models.grades import Grade
        if isinstance(grade, Grade):
            self.grades[grade.id] = grade

    def get_grade(self, grade_id: int):
        """Retrieve a grade by its ID."""
        return self.grades.get(grade_id)

    def remove_grade(self, grade_id: int):
        """Remove a grade by its ID."""
        if grade_id in self.grades:
            del self.grades[grade_id]

    def get_grades_by_student(self, student_id: int, subject: str = None):
        """Retrieve all grades for a specific student, optionally filtered by subject."""
        grades = [grade for grade in self.grades.values() if grade.student_id == student_id]
        if subject:
            grades = [grade for grade in grades if grade.subject == subject]
        return grades
    
    def calculate_grade_statistics_by_student(self, student_id: int, subject: str = None) -> Dict[str, float]:
        """Calculate average, highest, and lowest grades for a student, optionally filtered by subject."""
        grades = self.get_grades_by_student(student_id, subject)
        if not grades:
            return {"average": 0.0, "highest": 0.0, "lowest": 0.0}

        grade_values = [grade.value for grade in grades]
        average = sum(grade_values) / len(grade_values)
        highest = max(grade_values)
        lowest = min(grade_values)

        return {
            "average": round(average, 2),
            "highest": float(highest),
            "lowest": float(lowest)
        }

    def calculate_grade_statistics_by_class(self, class_id: str, subject: str = None) -> Dict[str, float]:
        """Calculate average, highest, and lowest grades for a class, optionally filtered by subject."""
        student_ids = self.get_students_by_class(class_id)
        all_grades = []
        for student_id in student_ids:
            grades = self.get_grades_by_student(student_id, subject)
            all_grades.extend([grade.value for grade in grades])

        if not all_grades:
            return {"average": 0.0, "highest": 0.0, "lowest": 0.0}

        average = sum(all_grades) / len(all_grades)
        highest = max(all_grades)
        lowest = min(all_grades)

        return {
            "average": round(average, 2),
            "highest": float(highest),
            "lowest": float(lowest)
        }

    def calculate_grade_statistics_by_subject(self, subject: str) -> Dict[str, float]:
        """Calculate average, highest, and lowest grades for a specific subject across all students."""
        grades = [grade for grade in self.grades.values() if grade.subject == subject]
        if not grades:
            return {"average": 0.0, "highest": 0.0, "lowest": 0.0}

        grade_values = [grade.value for grade in grades]
        average = sum(grade_values) / len(grade_values)
        highest = max(grade_values)
        lowest = min(grade_values)

        return {
            "average": round(average, 2),
            "highest": float(highest),
            "lowest": float(lowest)
        }
    
    # New Method for Viewing Student Progress
    def view_student_progress(self, student_id: int, subject: str = None) -> Dict:
        """
        View a student's academic progress, including grades, assignments, and statistics.
        
        Args:
            student_id (int): ID of the student.
            subject (str, optional): Filter progress by subject (e.g., "Math").
        
        Returns:
            Dict: Summary of the student's progress, including grades, assignment status, and statistics.
        """
        from core.student import Student
        student = self.get_user(student_id)
        if not isinstance(student, Student):
            return {"error": "Student not found or invalid ID"}

        # Get grades
        grades = self.get_grades_by_student(student_id, subject)
        grades_info = [grade.get_grade_info() for grade in grades]

        # Get assignments
        assignments = self.get_assignments_by_student(student_id)
        assignment_status = []
        total_assignments = 0
        submitted_assignments = 0
        for assignment in assignments:
            if subject and assignment.subject != subject:
                continue
            total_assignments += 1
            status = student.assignments.get(assignment.id, {"status": "Not Assigned", "content": ""})
            if status["status"] == "Submitted":
                submitted_assignments += 1
            assignment_status.append({
                "assignment_id": assignment.id,
                "title": assignment.title,
                "subject": assignment.subject,
                "deadline": assignment.deadline,
                "status": status["status"],
                "grade": assignment.grades.get(student_id, None)
            })

        # Calculate completion rate
        completion_rate = (submitted_assignments / total_assignments * 100) if total_assignments > 0 else 0.0

        # Get statistics
        stats = self.calculate_grade_statistics_by_student(student_id, subject)

        return {
            "student_id": student_id,
            "full_name": student._full_name,
            "class_id": student.grade,
            "grades": grades_info,
            "assignments": assignment_status,
            "completion_rate": round(completion_rate, 2),
            "statistics": stats
        }
    
    def add_parent_child(self, parent_id: int, child_id: int) -> bool:
        """Add a child to a parent's list of children."""
        from core.parent import Parent
        parent = self.get_user(parent_id)
        if isinstance(parent, Parent):
            if child_id not in parent.children:
                parent.children.append(child_id)
                return True
        return False