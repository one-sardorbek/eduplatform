from core.student import Student
from core.teacher import Teacher
from core.admin import Admin
from core.parent import Parent
from data.storage import DataStorage 
from models.schedule import Schedule
from models.assignments import Assignment
from models.grades import Grade
from models.notifications import Notification, Priority
from utils.auth import hash_password, authenticate_user
from utils.export import export_data
from utils.validation import validate_class_id, validate_time_slot
from datetime import datetime, time

def main():
    
    storage=DataStorage()
    student = Student(1, "Ali Valiev", "ali@example.com", hash_password("pass123"), "9-A")
    teacher = Teacher(2, "Nodira Teacher", "nodira@example.com", hash_password("teach123"))
    teacher.subjects = ["Math", "Physics"]
    teacher.classes = ["9-A"]
    parent = Parent(3, "Ota Ona", "parent@example.com", hash_password("parent123"))
    parent.add_child(child_id=1,storage=storage)
    admin = Admin(4, "Admin User", "admin@example.com", hash_password("admin123"))
    
    storage.add_user(student)
    storage.add_user(teacher)
    storage.add_user(parent)
    storage.add_user(admin)

    print(f"\nStarting at {datetime.now().strftime('%I:%M %p +05 on %B %d, %Y')}")
    creds = authenticate_user("admin@example.com", "admin123", storage)
    if creds and creds[1] == "Admin":
        admin_id = creds[0]
        print(f"Admin {admin_id} authenticated successfully")
    else:
        print("Authentication failed")
        return

    print("\n--- Admin Actions ---")
    new_student = Student(5, "New Student", "new@example.com", hash_password("pass567"), "10-B")
    success, message = admin.add_user(new_student, storage)
    print(f"Add student: {message}")

    schedule = Schedule(id=1, class_id="9-A", day="Friday")
    if validate_time_slot("09:00-09:45"):
        schedule.add_lesson("09:00-09:45", "Math", 2)
    if validate_time_slot("10:00-10:45"):
        schedule.add_lesson("10:00-10:45", "Physics", 2)
    success, message = admin.add_schedule(schedule, storage)
    print(f"Add schedule: {message}")


    print("\n--- Teacher Actions ---")
    
    assignment= Assignment(id=1, title="Math Homework", description="Solve equations 1-10", deadline="2025-06-15T23:59:00", subject="Math", teacher_id=teacher.id, class_id='9-A')
    teacher.create_assignment(assignment=assignment,storage=storage)
    if assignment.id in storage.assignments:
        print(f"Created assignment {assignment.id} for class {assignment.class_id}")
   
    
    print("\n--- Student Actions ---")
    student.submit_assignment(assignment_id=1, content="Here is my solution",storage=storage)
    print(f"Student {student.full_name} submitted assignment {assignment.id}")

    print("\n--- Teacher Actions ---")
    teacher.view_student_submissions(student_id=1, assignment_id=1, storage=storage)
    teacher.grade_assignment(assignment_id=1, student_id=1, grade=4, storage=storage)
    print(f"Graded assignment 1 for student {student.id} with grade 4")


    notifications = parent.receive_child_notification(child_id=1,storage=storage,generate_new =True)
    print("\n--- Parent Notifications ---")
    for notif in notifications:
        print(f"Notification: {notif['message']} (Priority: {notif['priority']})")

    print("\n--- Exporting Data ---")
    success = admin.export_data(storage, "csv")
    print(f"Export to CSV: {'Successful' if success else 'Failed'}")

    print("\n--- All Users ---")
    users = admin.view_all_users(storage)
    for user in users:
        print(f"User: {user['full_name']} (Role: {user['role']})")

    admin.remove_schedule(1, storage)
    print(f"\nRemoved schedule ID 1: {'Success' if 1 not in storage.schedules else 'Failed'}")

if __name__ == "__main__":
    main()