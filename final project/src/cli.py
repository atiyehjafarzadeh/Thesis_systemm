import os
import auth, services

# --- Global variable for logged in user ---
current_user = None
user_type = None

# --- Helper Functions ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_for_enter():
    input("\nبرای بازگشت به منو، کلید Enter را فشار دهید...")

# --- Main Menus ---
def main_menu():
    global current_user, user_type
    while True:
        clear_screen()
        print("به سامانه مدیریت پایان‌نامه‌ها خوش آمدید")
        print("="*40)
        if current_user:
            print(f"کاربر فعلی: {current_user['name']} ({'دانشجو' if user_type == 'student' else 'استاد'})")
            if user_type == 'student':
                student_menu()
            else:
                professor_menu()
        else:
            print("1. ورود به عنوان دانشجو")
            print("2. ورود به عنوان استاد")
            print("3. جستجو در آرشیو پایان‌نامه‌ها")
            print("4. خروج")
            choice = input("> ")
            if choice == '1':
                login_menu('student')
            elif choice == '2':
                login_menu('professor')
            elif choice == '3':
                search_menu()
            elif choice == '4':
                print("خداحافظ!")
                break

def login_menu(u_type):
    global current_user, user_type
    user_type = u_type
    print(f"\n--- ورود به عنوان {'دانشجو' if u_type == 'student' else 'استاد'} ---")
    user_id = input(f"کد {'دانشجویی' if u_type == 'student' else 'استادی'}: ")
    password = input("رمز عبور: ")
    user_data = auth.login(user_type, user_id, password)
    if user_data:
        current_user = user_data
        print("ورود با موفقیت انجام شد!")
    else:
        user_type = None
        print("نام کاربری یا رمز عبور اشتباه است.")
    wait_for_enter()

def logout():
    global current_user, user_type
    current_user = None
    user_type = None
    print("شما با موفقیت از سیستم خارج شدید.")
    wait_for_enter()

# --- Student Menu ---
def student_menu():
    while current_user:
        clear_screen()
        print(f"--- منوی دانشجو: {current_user['name']} ---")
        print("1. درخواست اخذ درس پایان‌نامه")
        print("2. مشاهده وضعیت درخواست‌ها")
        print("3. ارسال درخواست دفاع")
        print("4. جستجو در آرشیو")
        print("5. تغییر رمز عبور")
        print("6. خروج از حساب کاربری")
        choice = input("> ")
        if choice == '1':
            request_thesis_course_view()
        elif choice == '2':
            view_student_requests_view()
        elif choice == '3':
            submit_defense_request_view()
        elif choice == '4':
            search_menu()
        elif choice == '5':
            change_password_view()
        elif choice == '6':
            logout()
            break
        else:
            print("گزینه نامعتبر است.")
            wait_for_enter()
    
# --- Professor Menu ---
def professor_menu():
     while current_user:
        clear_screen()
        print(f"--- منوی استاد: {current_user['name']} ---")
        print("1. مشاهده و بررسی درخواست‌های راهنمایی")
        print("2. مشاهده و تایید درخواست‌های دفاع")
        print("3. مشاهده دفاع‌های تخصیص یافته (داوری)")
        print("4. ثبت نمره")
        print("5. جستجو در آرشیو")
        print("6. تغییر رمز عبور")
        print("7. خروج از حساب کاربری")
        choice = input("> ")
        if choice == '1':
            manage_supervision_requests_view()
        elif choice == '2':
            manage_defense_requests_view()
        elif choice == '3':
            view_assigned_defenses_view()
        elif choice == '4':
            submit_grade_view()
        elif choice == '5':
            search_menu()
        elif choice == '6':
            change_password_view()
        elif choice == '7':
            logout()
            break
        else:
            print("گزینه نامعتبر است.")
            wait_for_enter()


# --- CLI Views ---
def request_thesis_course_view():
    clear_screen()
    print("--- لیست دروس پایان‌نامه دارای ظرفیت ---")
    courses = services.get_available_courses()
    if not courses:
        print("در حال حاضر هیچ درسی با ظرفیت خالی وجود ندارد.")
    else:
        for c in courses:
            print(f"ID: {c['course_id']}, عنوان: {c['title']}, استاد: {c['professor_id']}, ظرفیت: {c['capacity']}")
        
        course_id = input("\nکد درس مورد نظر را وارد کنید: ")
        success, message = services.submit_thesis_request(current_user['user_id'], course_id)
        print(message)
    wait_for_enter()

def view_student_requests_view():
    clear_screen()
    print("--- وضعیت درخواست‌های شما ---")
    requests = services.get_student_request_status(current_user['user_id'])
    if not requests:
        print("شما هیچ درخواستی ثبت نکرده‌اید.")
    else:
        for r in requests:
            print(f"ID درخواست: {r['request_id']}, کد درس: {r['course_id']}, وضعیت: {r['status']}")
    wait_for_enter()

def submit_defense_request_view():
    clear_screen()
    print("--- ثبت درخواست دفاع ---")
    title = input("عنوان پایان‌نامه: ")
    abstract = input("چکیده: ")
    keywords = input("کلمات کلیدی (با کاما جدا کنید): ")
    pdf_path = input("مسیر فایل PDF پایان‌نامه: ")
    image_path = input("مسیر فایل تصویر صفحه اول: ")

    success, message = services.submit_defense_request(
        current_user['user_id'], title, abstract, keywords, pdf_path, image_path
    )
    print(message)
    wait_for_enter()

def manage_supervision_requests_view():
    clear_screen()
    print("--- درخواست‌های راهنمایی در انتظار تایید ---")
    requests = services.get_supervision_requests(current_user['user_id'])
    if not requests:
        print("هیچ درخواست جدیدی وجود ندارد.")
    else:
        for r in requests:
            print(f"ID: {r['request_id']}, دانشجوی متقاضی: {r['student_id']}")
        
        req_id = input("\nID درخواست جهت بررسی را وارد کنید: ")
        action = input("تایید (approve) یا رد (reject) می‌کنید؟ ")
        if action in ['approve', 'reject']:
            success, message = services.process_supervision_request(current_user['user_id'], req_id, action)
            print(message)
        else:
            print("عملیات نامعتبر است.")
    wait_for_enter()

def manage_defense_requests_view():
    clear_screen()
    print("--- درخواست‌های دفاع در انتظار تایید ---")
    requests = services.get_defense_requests(current_user['user_id'])
    if not requests:
        print("هیچ درخواست دفاعی وجود ندارد.")
    else:
        for r in requests:
            print(f"ID: {r['request_id']}, دانشجو: {r['student_id']}, عنوان: {r['details']['title']}")
        
        req_id = input("\nID درخواست دفاع جهت تایید را وارد کنید: ")
        defense_date = input("تاریخ دفاع را وارد کنید (YYYY-MM-DD): ")
        internal_examiner = input("کد استاد داور داخلی: ")
        external_examiner = input("کد استاد داور خارجی: ")
        
        success, message = services.process_defense_request(
            current_user['user_id'], req_id, defense_date, internal_examiner, external_examiner
        )
        print(message)

    wait_for_enter()
    
def view_assigned_defenses_view():
    clear_screen()
    print("--- جلسات دفاع تخصیص یافته به شما برای داوری ---")
    theses = services.get_assigned_defenses(current_user['user_id'])
    if not theses:
        print("هیچ جلسه دفاعی برای شما ثبت نشده است.")
    else:
        for t in theses:
            print(f"ID پایان‌نامه: {t['thesis_id']}, دانشجو: {t['student_id']}, عنوان: {t['title']}, تاریخ دفاع: {t['defense_date']}")
    wait_for_enter()

def submit_grade_view():
    clear_screen()
    print("--- ثبت نمره نهایی دفاع ---")
    theses = services.get_assigned_defenses(current_user['user_id'])
    if not theses:
        print("هیچ دفاعی برای نمره‌دهی وجود ندارد.")
    else:
        for t in theses:
             print(f"ID پایان‌نامه: {t['thesis_id']}, دانشجو: {t['student_id']}")
        
        thesis_id = input("\nID پایان‌نامه‌ای که می‌خواهید نمره دهید را وارد کنید: ")
        try:
            score = int(input("نمره خود را از ۱۰۰ وارد کنید: "))
            if 0 <= score <= 100:
                success, message = services.submit_grade(thesis_id, current_user['user_id'], score)
                print(message)
            else:
                print("نمره باید بین ۰ تا ۱۰۰ باشد.")
        except ValueError:
            print("لطفا یک عدد صحیح وارد کنید.")
    wait_for_enter()
    
def search_menu():
    clear_screen()
    print("--- جستجو در آرشیو پایان‌نامه‌ها ---")
    print("جستجو بر اساس: 1. عنوان (title) 2. نویسنده (author) 3. استاد راهنما (supervisor) 4. کلمات کلیدی (keywords)")
    choice = input("> ")
    search_by_map = {'1': 'title', '2': 'author', '3': 'supervisor', '4': 'keywords'}
    
    if choice in search_by_map:
        search_by = search_by_map[choice]
        query = input(f"عبارت مورد نظر برای جستجو بر اساس '{search_by}' را وارد کنید: ")
        results = services.search_theses(query, search_by)
        
        if not results:
            print("هیچ نتیجه‌ای یافت نشد.")
        else:
            print("\n--- نتایج جستجو ---")
            for r in results:
                print(f"عنوان: {r['title']}, نویسنده: {r['student_id']}, استاد راهنما: {r['supervisor_id']}, نمره: {r['grade']}")
                print(f"  چکیده: {r['abstract'][:100]}...")
                print("-" * 20)
    else:
        print("گزینه نامعتبر است.")
    wait_for_enter()

def change_password_view():
    clear_screen()
    print("--- تغییر رمز عبور ---")
    new_password = input("رمز عبور جدید را وارد کنید: ")
    confirm_password = input("رمز عبور جدید را تکرار کنید: ")
    if new_password == confirm_password:
        success = auth.change_password_in_db(user_type, current_user['user_id'], new_password)
        if success:
            print("رمز عبور با موفقیت تغییر کرد.")
        else:
            print("خطایی در تغییر رمز عبور رخ داد.")
    else:
        print("رمزهای عبور مطابقت ندارند.")
    wait_for_enter()