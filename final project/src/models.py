from abc import ABC, abstractmethod

class User(ABC):
    """کلاس پایه برای تمام کاربران سیستم."""
    def __init__(self, user_id, name, password_hash):
        self.user_id = user_id
        self.name = name
        self.password_hash = password_hash

    @abstractmethod
    def get_dashboard(self):
        pass

class Student(User):
    """کلاس نمایانگر یک دانشجو."""
    def __init__(self, user_id, name, password_hash):
        super().__init__(user_id, name, password_hash)

    def get_dashboard(self):
        return f"داشبورد دانشجو: {self.name} ({self.user_id})"

class Professor(User):
    """کلاس نمایانگر یک استاد."""
    def __init__(self, user_id, name, password_hash, supervision_capacity, examiner_capacity):
        super().__init__(user_id, name, password_hash)
        self.supervision_capacity = supervision_capacity
        self.examiner_capacity = examiner_capacity

    def get_dashboard(self):
        return (f"داشبورد استاد: {self.name} ({self.user_id})\n"
                f"ظرفیت راهنمایی: {self.supervision_capacity}\n"
                f"ظرفیت داوری: {self.examiner_capacity}")

class ThesisCourse:
    """کلاس نمایانگر درس پایان‌نامه."""
    def __init__(self, course_id, title, professor_id, year, semester, capacity, unit):
        self.course_id = course_id
        self.title = title
        self.professor_id = professor_id
        self.year = year
        self.semester = semester
        self.capacity = capacity
        self.unit = unit