from django.shortcuts import render
from django.db import transaction  # to rollback data from database
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.http import HttpResponse, JsonResponse
import random
from django.core.mail import EmailMessage
from main_app.helper import save_activity
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from rest_framework.authtoken.models import Token
import uuid
from django.utils import timezone


# <-----------  Start Registration View  ----------->
def register(request):
    print("register views")
    return render(request, 'main_app/register.html')

@csrf_exempt
def otp(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                email = request.POST.get('email')
                pwd = request.POST.get('password')
                
                if User.objects.filter(email=email).exists():
                    return render(request, 'main_app/register.html', {'response': 'Failed', 'msg': 'User Already Exists'})
                else:
                    user = User.objects.create(
                        email=email,
                        password=pwd,
                        first_name=first_name,
                        last_name=last_name,
                        is_active=False,
                    )
                    group = Group.objects.get(name='Institutes Group')
                    level = Level.objects.create(user=user, level='Institute Admin')
                    Role.objects.create(user=user, group=group, level=level)

                    otp = random.randint(100000, 999999)
                    if otp is not None:
                        msg = f'''
                            Hi {user.first_name} {user.last_name},

                            Thanks for creating an account on CloveERP by SixthClover Technologies Pvt Ltd. Here is the one-time password to verify your email address,

                            OTP - {otp}

                            Use the above OTP to verify your account.

                            Thanks,
                            Team CloveERP
                        '''
                        mail1 = EmailMessage(
                            'CloveERP - OTP Account Verification', body=msg, to=[user.email])
                        mail1.content_subtype = 'html'
                        mail1.send()
                        request.session['otp'] = otp
                        request.session['user'] = user.id

                        module = 'CloveERP Registration'
                        sub_module = 'Registration'
                        heading = 'Try to create Registration for Institution'
                        activity_msg = ' Registration Successfully Done'
                        user_id = user.id
                        icon = 'Register'
                        platform = 0
                        platform_icon = 'Register Admin'
                        save_activity(module, sub_module, heading, activity_msg, user_id, email, icon, platform, platform_icon)

                        context = {
                            "msg": "OTP Generated Successfully!"
                        }
                        return render(request, 'main_app/otp.html', context)
        except Exception as e:
            print(f"Exception: {str(e)}")
            transaction.rollback()
            return redirect('/register/', {"msg": "Message : OTP Not Generated"})
    else:
        print("else otp views")
        return redirect('/register/', {"msg": "Message : OTP Not Generated"})

def resend_otp(request):
    user = User.objects.get(id=request.session.get('user'))
    otp = random.randint(100000, 999999)
    msg = '''
    Hi '''+user.first_name+" "+user.last_name+'''

    Thanks for creating an account on CloveERP by SixthClover Technologies Pvt Ltd. Here is the one time password to verify your email address,

    OTP - '''+str(otp)+'''

    Use the above OTP to verify your account.

    Thanks,
    Team CloveERP
    '''
    request.session['otp'] = otp

    EmailMessage('CloveERP - OTP Account Verification', msg, to=[user.email]).send()
    return render(request, 'main_app/otp.html', {"msg" : "OTP Resent Successfully"})

@csrf_exempt
def verify_otp(request):
    if request.method == 'POST':
        otp = request.session.get('otp')
        otp2 = request.POST.get('otp')
        user_id = request.session.get('user')
        if str(otp) == otp2:
            User.objects.filter(id=user_id).update(is_active=True)
            user = User.objects.get(id=user_id)
            print(user)
            msg = f'''
                Hi {user.first_name} {user.last_name},

                Your Account is Created Successfully.
                
                Just 1 step left!

                Thanks,
                Team CloveERP
            '''
            mail = EmailMessage('CloveERP - OTP Account Verification', body=msg, to=[user.email])
            mail.content_subtype = 'html'
            mail.send()
            return redirect("/pricing_plan/")
        return render(request, "main_app/otp.html", {'msg': 'Invalid OTP Entered'})
    return render(request, 'main_app/register.html')


def pricing_plan(request):
    user = User.objects.get(id=request.session.get('user'))
    return render(request, "main_app/pricing_plan.html", {'user': user})

def selected_plan(request, slug):
    user = User.objects.get(id=request.session.get('user'))
    print(user, "-----> user")
    plan = PricingPlan(user=user)
    if slug == "EXPERT":
        print("Expert Slug")
        plan.plan = slug
        plan.is_active = True
        plan.price = 59.99
        plan.save()
        return redirect('/', {'msg': slug})
    elif slug == "PRO":
        print("Pro Slug")
        plan.plan = slug
        plan.is_active = True
        plan.price = 99.99
        plan.save()
        return redirect('/', {'msg': slug})
    elif slug == "GURU":
        print("Guru Slug")
        plan.plan = slug
        plan.is_active = True
        plan.price = 199.99
        plan.save()
        return redirect('/', {'msg': "Account Created Successfully"})
    else:
        return redirect('pricing_plan', {'msg': 'Select a CloveERP Pricing Plan', "user": user})
    
# <-----------  End Registration View  ----------->

@csrf_exempt
def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        pwd = request.POST.get('password')
        print(email)
        print(pwd)
        if User.objects.filter(email=email).exists():
            print('Here i am')
            if User.objects.filter(email=email, is_active=True).exists():
                chk_user = User.objects.get(email=email)
                print(chk_user)
                print(chk_user.password)
                user = authenticate(request, username=chk_user.email, password=pwd)
                print(user)
                print('Here i again')
                if user is not None:
                    login(request, user)
                    return redirect('/dashboard/')
    return render(request, 'main_app/login.html')

# @csrf_exempt
# def login_user(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         pwd = request.POST.get('password')
#         print(email)
#         print(pwd)
#         if User.objects.filter(email=email).exists():
#             print('Here i am')
#             if User.objects.filter(email=email, is_active=True).exists():
#                 chk_user = User.objects.get(email=email)
#                 print(chk_user)
#                 print(chk_user.password)
#                 user = authenticate(request, username=chk_user.username, password=pwd)
#                 print(user)
#                 print('Here i am2')
#                 if user is not None:
#                     login(request, user)
#                     if request.user.is_superuser:
#                         return redirect('admin_dashboard')
#                     else:
#                         print('Here')
#                         try:
#                             if request.user.role.level.level == 'Store Admin':
#                                 print(
#                                     'SSSSSSSSSST^TTTTTTTTTTTTOOOOOOOOOOORRRRRRRRRRRRRRREEEEEEEEEEEEEEEE')

#                                 license = None
#                                 try:
#                                     license = Licsense.objects.get(
#                                         user=user, status=True, paid=True)
#                                 except Licsense.DoesNotExist:
#                                     return redirect('/buylicense/')
#                                 l_date = license.license_date
#                                 delta = l_date + timedelta(days=license.days)
#                                 now = timezone.now()
#                                 remaining_days = delta - now
#                                 if remaining_days.days <= 0:
#                                     license.status = False
#                                     license.paid = False
#                                     license.save()
#                                 if Licsense.objects.filter(user=user, status=True, paid=True).exists():
#                                     print("jjjjjjjjjjjjjj")
#                                     module = 'Login'
#                                     sub_module = 'Admin Login'
#                                     heading = 'Admin Login Welcome TO ERP'
#                                     activity_msg = 'try to login and login successfully'
#                                     user_id = (request.user.id)
#                                     user_name = (request.user.username)
#                                     icon = 'login'
#                                     platform = 0
#                                     platform_icon = 'web-login by admin'
#                                     save_activity(module, sub_module, heading, activity_msg,
#                                                   user_id, user_name, icon, platform, platform_icon)
#                                     return redirect('dashboard_page')
#                                 else:
#                                     return redirect('/buylicense/')
#                             elif request.user.store_role.level.level == 'HR Head':
#                                 print('HHHHHHHHHEEEEEEEERRRRRRRRRRRRRRRRRRRRRR')
#                                 return redirect('/hrm/dashboard')
                               
#                             else:
#                                 messages.success(
#                                     request, 'User has no role. Contact ERP Admin')
#                                 return redirect('logout_page')
#                         except:
#                             return render(request, '401.html')

#                 else:
#                     messages.info(request, 'Incorrect Password')
#                     return redirect('login_page')
#             else:
#                 messages.info(request, 'Email Not Verified')
#                 return redirect('login_page')
#         else:
#             messages.info(request, 'Incorrect Email')
#             return redirect('login_page')
#     if request.user.is_authenticated:
#         return redirect('dashboard_page')
#     else:
#         return render(request, 'main_app/login.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def add_books(request):
    return render(request, 'add-books.html')

def add_department(request):
    return render(request, 'add-department.html')

def add_events(request):
    return render(request, 'add-events.html')

def add_exam(request):
    return render(request, 'add-exam.html')

def add_expenses(request):
    return render(request, 'add-expenses.html')

def add_fees_collection(request):
    return render(request, 'add-fees-collection.html')

def add_fees(request):
    return render(request, 'add-fees.html')

def add_holiday(request):
    return render(request, 'add-holiday.html')

def add_room(request):
    return render(request, 'add-room.html')

def add_salary(request):
    return render(request, 'add-salary.html')

def add_sports(request):
    return render(request, 'add-sports.html')

def add_student(request):
    return render(request, 'add-student.html')

def add_subject(request):
    return render(request, 'add-subject.html')

def add_teacher(request):
    return render(request, 'add-teacher.html')

def add_time_table(request):
    return render(request, 'add-time-table.html')

def add_transport(request):
    return render(request, 'add-transport.html')

def components(request):
    return render(request, 'components.html')

def compose(request):
    return render(request, 'compose.html')

def data_tables(request):
    return render(request, 'data-tables.html')

def departments(request):
    return render(request, 'departments.html')

def edit_books(request):
    return render(request, 'edit-books.html')

def edit_departments(request):
    return render(request, 'edit-department.html')

def edit_exam(request):
    return render(request, 'edit-exam.html')

def edit_fees(request):
    return render(request, 'edit-fees.html')

def edit_room(request):
    return render(request, 'edit-room.html')

def edit_sports(request):
    return render(request, 'edit-sports.html')

def edit_student(request):
    return render(request, 'edit-student.html')

def edit_subject(request):
    return render(request, 'edit-subject.html')

def edit_teacher(request):
    return render(request, 'edit-teacher.html')

def edit_time_table(request):
    return render(request, 'edit-time-table.html')

def edit_transport(request):
    return render(request, 'edit-transport.html')

def error_404(request):
    return render(request, 'error-404.html')

def event(request):
    return render(request, 'event.html')

def exam(request):
    return render(request, 'exam.html')

def expenses(request):
    return render(request, 'expenses.html')

def fees_collections(request):
    return render(request, 'fees-collections.html')

def fees(request):
    return render(request, 'fees.html')

def forgot_password(request):
    return render(request, 'forgot-password.html')

def form_basic_inputs(request):
    return render(request, 'form-basic-inputs.html')

def form_horizontal(request):
    return render(request, 'form-horizontal.html')

def form_input_groups(request):
    return render(request, 'form_input_groups.html')

def form_mask(request):
    return render(request, 'form-mask.html')

def form_validation(request):
    return render(request, 'form-validation.html')

def form_vertical(request):
    return render(request, 'form-vertical.html')

def holiday(request):
    return render(request, 'holiday.html')

def hostel(request):
    return render(request, 'hostel.html')

def inbox(request):
    return render(request, 'inbox.html')

def invoice(request):
    return render(request, 'invoice.html')

def library(request):
    return render(request, 'library.html')

def profile(request):
    return render(request, 'profile.html')

def salary(request):
    return render(request, 'salary.html')

def sports(request):
    return render(request, 'sports.html')

def student_dashboard(request):
    return render(request, 'student-dashboard.html')

def student_details(request):
    return render(request, 'student-details.html')

def students(request):
    return render(request, 'students.html')

def subjects(request):
    return render(request, 'subjects.html')

def tables_basic(request):
    return render(request, 'tables-basic.html')

def teacher_dashboard(request):
    return render(request, 'teacher-dashboard.html')

def teacher_details(request):
    return render(request, 'teacher-details.html')

def teachers(request):
    return render(request, 'teachers.html')

def time_table(request):
    return render(request, 'time-table.html')

def transport(request):
    return render(request, 'transport.html')

def blank_page(request):
    return render(request, 'blank-page.html')
