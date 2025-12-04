# Bibliotecas de Terceiros (Third-Party / Django)
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model

# Importações Locais (Local App)
from .forms import SessionForm, UserForm, StudentRegistrationForm
from .models import Session, Student, User

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'authentication/sign-in.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def register_users(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['name'],
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                birth_date=form.cleaned_data['birth_date'],
                gender=form.cleaned_data['gender'],
                phone=form.cleaned_data['phone']
            )
            return redirect('login')

@login_required
def index(request):
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = SessionForm()
    
    now = timezone.localdate()
    
    search_query = request.GET.get('q', '')
    
    sessions_list = Session.objects.all().order_by('date', 'time').reverse()
    
    if search_query:
        sessions_list = sessions_list.filter(
            Q(students__user__name__icontains=search_query) | 
            Q(place__icontains=search_query) |
            Q(notes__icontains=search_query)
        ).distinct()

    paginator = Paginator(sessions_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    sessions_per_month = Session.objects.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    chart_months = [entry['month'].strftime('%b') for entry in sessions_per_month]
    chart_counts = [entry['count'] for entry in sessions_per_month]
    
    context = {
        'sessions': page_obj,
        'students': Student.objects.count(),
        'today_sessions': Session.objects.filter(date=now).count(),
        'chart_months': chart_months,
        'chart_counts': chart_counts,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard.html', {'form': form, 'context': context})

def delete_session(session_id):
    session = get_object_or_404(Session, id=session_id)
    session.delete()
    return redirect('index')

def login_professor_aee(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'index'
            return redirect(next_url)
        else:
            error_message = 'Email or password invalid.'

    return render(request, 'authentication/login_professor_aee.html', {'error': error_message})

@login_required
def profile_view(request, pk):
    student_obj = get_object_or_404(Student, pk=pk)
    return render(request, 'students/profile.html', {'student': student_obj})

@login_required
def student_list(request):
    search_query = request.GET.get('q', '')
    
    students = Student.objects.all().order_by('user__name')
    
    if search_query:
        students = students.filter(
            Q(user__name__icontains=search_query) |
            Q(enrollment_number__icontains=search_query) |
            Q(course__icontains=search_query)
        ).distinct()
        
    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'students': page_obj,
        'search_query': search_query,
        'page_range': page_obj.paginator.page_range,
    }
    
    return render(request, 'students/student_list.html', context)

@login_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        user = student.user
        student.delete()
        user.delete()
        messages.success(request, 'Aluno excluído com sucesso.')
        return redirect('student_list')

@login_required
def create_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                with transaction.atomic():
                    user = User.objects.create(
                        name=data['name'],
                        email=data['email'],
                        birth_date=data['birth_date'],
                        gender=data['gender'],
                        birth_place=data['birth_place'],
                        phone=data['phone'],
                        username=data['email']
                    )
                    user.set_password(data['password'])
                    user.save()

                    Student.objects.create(
                        user=user,
                        enrollment_number=data['enrollment_number'],
                        parent=data['parent'],
                        course=data['course']
                    )
                    messages.success(request, 'Aluno cadastrado com sucesso.')
                    return redirect('student_list')
            except Exception as e:
                messages.error(request, f"Erro ao cadastrar aluno: {e}")
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'students/create_student.html', {'form': form})
    return redirect('student_list')