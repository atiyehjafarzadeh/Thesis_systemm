import uuid
from datetime import datetime, timedelta
from database import load_data, save_data

# --- Helper Functions ---
def find_item_by_id(item_list, item_id, id_key='id'):
    """یک آیتم را بر اساس شناسه در یک لیست پیدا می‌کند."""
    for item in item_list:
        if item.get(id_key) == item_id:
            return item
    return None

# --- Student Services ---
def get_available_courses():
    """لیست دروس پایان‌نامه دارای ظرفیت را برمی‌گرداند."""
    courses = load_data('courses.json')
    return [c for c in courses if c.get('capacity', 0) > 0]

def submit_thesis_request(student_id, course_id):
    """درخواست اخذ درس پایان‌نامه را برای دانشجو ثبت می‌کند."""
    requests = load_data('requests.json')
    courses = load_data('courses.json')

    # بررسی اینکه آیا دانشجو درخواست فعال دیگری دارد یا خیر
    if any(r['student_id'] == student_id and r['status'] != 'رد شده' for r in requests):
        return False, "شما در حال حاضر یک درخواست فعال یا تایید شده دارید."

    course = find_item_by_id(courses, course_id, 'course_id')
    if not course or course['capacity'] <= 0:
        return False, "درس مورد نظر یافت نشد یا ظرفیت آن تکمیل است."

    new_request = {
        "request_id": str(uuid.uuid4()),
        "type": "course_request",
        "student_id": student_id,
        "course_id": course_id,
        "professor_id": course['professor_id'],
        "request_date": datetime.now().isoformat(),
        "status": "در انتظار تأیید استاد"
    }
    requests.append(new_request)
    save_data('requests.json', requests)
    return True, "درخواست شما با موفقیت ثبت و برای استاد ارسال شد."

def get_student_request_status(student_id):
    """وضعیت درخواست‌های یک دانشجو را برمی‌گرداند."""
    requests = load_data('requests.json')
    student_requests = [r for r in requests if r.get('student_id') == student_id and r.get('type') == 'course_request']
    return student_requests

def submit_defense_request(student_id, title, abstract, keywords, pdf_path, image_path):
    """درخواست دفاع را برای دانشجو ثبت می‌کند."""
    requests = load_data('requests.json')
    
    # یافتن درخواست تایید شده دانشجو
    approved_request = next((r for r in requests if r['student_id'] == student_id and r['status'] == 'تأیید شده'), None)
    
    if not approved_request:
        return False, "شما درس پایان‌نامه تایید شده‌ای ندارید."

    approval_date = datetime.fromisoformat(approved_request['approval_date'])
    if datetime.now() < approval_date + timedelta(days=90):
        return False, "باید حداقل ۳ ماه از تاریخ تایید درس شما گذشته باشد."

    new_defense_req = {
        "request_id": str(uuid.uuid4()),
        "type": "defense_request",
        "student_id": student_id,
        "course_request_id": approved_request['request_id'],
        "professor_id": approved_request['professor_id'],
        "submission_date": datetime.now().isoformat(),
        "status": "در انتظار تأیید استاد",
        "details": {
            "title": title,
            "abstract": abstract,
            "keywords": keywords,
            "pdf_path": pdf_path,
            "image_path": image_path
        }
    }
    requests.append(new_defense_req)
    save_data('requests.json', requests)
    return True, "درخواست دفاع شما با موفقیت ثبت شد."

# --- Professor Services ---
def get_supervision_requests(professor_id):
    """لیست درخواست‌های راهنمایی برای یک استاد را برمی‌گرداند."""
    requests = load_data('requests.json')
    return [r for r in requests if r['professor_id'] == professor_id and r['type'] == 'course_request' and r['status'] == 'در انتظار تأیید استاد']

def process_supervision_request(professor_id, request_id, action):
    """یک درخواست راهنمایی را تایید یا رد می‌کند."""
    requests = load_data('requests.json')
    professors = load_data('professors.json')
    courses = load_data('courses.json')

    request = find_item_by_id(requests, request_id, 'request_id')
    professor = find_item_by_id(professors, professor_id, 'user_id')

    if not request or request['professor_id'] != professor_id:
        return False, "درخواست یافت نشد."

    if action == 'approve':
        if professor['supervision_capacity'] <= 0:
            return False, "ظرفیت راهنمایی شما تکمیل است."
        
        request['status'] = 'تأیید شده'
        request['approval_date'] = datetime.now().isoformat()
        professor['supervision_capacity'] -= 1
        
        course = find_item_by_id(courses, request['course_id'], 'course_id')
        if course:
            course['capacity'] -= 1

    elif action == 'reject':
        request['status'] = 'رد شده'
    else:
        return False, "عملیات نامعتبر است."

    save_data('requests.json', requests)
    save_data('professors.json', professors)
    save_data('courses.json', courses)
    return True, f"درخواست با موفقیت { 'تأیید' if action == 'approve' else 'رد' } شد."

def get_defense_requests(professor_id):
    """لیست درخواست‌های دفاع برای یک استاد راهنما را برمی‌گرداند."""
    requests = load_data('requests.json')
    return [r for r in requests if r['professor_id'] == professor_id and r['type'] == 'defense_request' and r['status'] == 'در انتظار تأیید استاد']

def process_defense_request(professor_id, request_id, defense_date, internal_examiner_id, external_examiner_id):
    """یک درخواست دفاع را تایید و اطلاعات جلسه دفاع را ثبت می‌کند."""
    requests = load_data('requests.json')
    theses = load_data('theses.json')
    professors = load_data('professors.json')

    request = find_item_by_id(requests, request_id, 'request_id')
    if not request or request['professor_id'] != professor_id:
        return False, "درخواست دفاع یافت نشد."

    # بررسی ظرفیت داوران
    internal_examiner = find_item_by_id(professors, internal_examiner_id, 'user_id')
    external_examiner = find_item_by_id(professors, external_examiner_id, 'user_id')

    if not internal_examiner or internal_examiner['examiner_capacity'] <= 0:
        return False, "داور داخلی یافت نشد یا ظرفیت داوری او تکمیل است."
    if not external_examiner or external_examiner['examiner_capacity'] <= 0:
        return False, "داور خارجی یافت نشد یا ظرفیت داوری او تکمیل است."

    # ایجاد پایان‌نامه نهایی
    new_thesis = {
        "thesis_id": str(uuid.uuid4()),
        "student_id": request['student_id'],
        "supervisor_id": professor_id,
        "title": request['details']['title'],
        "abstract": request['details']['abstract'],
        "keywords": request['details']['keywords'],
        "pdf_path": request['details']['pdf_path'],
        "image_path": request['details']['image_path'],
        "defense_date": defense_date,
        "examiners": [internal_examiner_id, external_examiner_id],
        "status": "تایید شده برای دفاع",
        "grade": None,
        "scores": {}
    }
    theses.append(new_thesis)
    
    # بروزرسانی ظرفیت‌ها و وضعیت درخواست
    request['status'] = 'تأیید نهایی شد'
    internal_examiner['examiner_capacity'] -= 1
    external_examiner['examiner_capacity'] -= 1

    save_data('requests.json', requests)
    save_data('theses.json', theses)
    save_data('professors.json', professors)
    
    return True, "جلسه دفاع با موفقیت ثبت شد."

def get_assigned_defenses(professor_id):
    """لیست دفاع‌هایی که استاد به عنوان داور در آن‌ها حضور دارد را برمی‌گرداند."""
    theses = load_data('theses.json')
    return [t for t in theses if professor_id in t['examiners'] and t['grade'] is None]

def submit_grade(thesis_id, examiner_id, score):
    """نمره داور برای یک پایان‌نامه را ثبت می‌کند."""
    theses = load_data('theses.json')
    professors = load_data('professors.json')

    thesis = find_item_by_id(theses, thesis_id, 'thesis_id')
    if not thesis:
        return False, "پایان‌نامه یافت نشد."

    thesis['scores'][examiner_id] = score
    
    # اگر هر دو داور نمره داده باشند، نمره نهایی را محاسبه و ظرفیت‌ها را آزاد کن
    if len(thesis['scores']) == 2:
        final_score = sum(thesis['scores'].values()) / 2
        grade_map = {range(90, 101): 'الف', range(80, 90): 'ب', range(70, 80): 'ج'}
        thesis['grade'] = next((g for r, g in grade_map.items() if final_score in r), 'د')
        thesis['status'] = 'دفاع شده'

        # آزاد کردن ظرفیت استاد راهنما
        supervisor = find_item_by_id(professors, thesis['supervisor_id'], 'user_id')
        if supervisor:
            supervisor['supervision_capacity'] += 1
        
        # آزاد کردن ظرفیت داوران
        for ex_id in thesis['examiners']:
            examiner = find_item_by_id(professors, ex_id, 'user_id')
            if examiner:
                examiner['examiner_capacity'] += 1
        
        save_data('professors.json', professors)

    save_data('theses.json', theses)
    return True, "نمره با موفقیت ثبت شد."

# --- Search Service ---
def search_theses(query, search_by):
    """جستجو در آرشیو پایان‌نامه‌ها."""
    theses = load_data('theses.json')
    results = []
    
    for thesis in theses:
        if thesis['status'] != 'دفاع شده':
            continue

        match = False
        if search_by == 'title' and query.lower() in thesis['title'].lower():
            match = True
        elif search_by == 'author' and query.lower() in thesis['student_id'].lower():
            match = True
        elif search_by == 'supervisor' and query.lower() in thesis['supervisor_id'].lower():
            match = True
        elif search_by == 'keywords' and query.lower() in thesis['keywords'].lower():
            match = True
        
        if match:
            results.append(thesis)
            
    return results