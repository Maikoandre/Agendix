# Bibliotecas Padrão (Standard Library)
from datetime import date, datetime

# Bibliotecas de Terceiros (Third-Party / Django)
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

# Importações Locais (Local App)
from .forms import ProfessorAEERegistrationForm, SessionForm, UserForm
from .models import Professor, ProfessorAEE, Session, Student, User

@login_required(login_url='login')
def index(request):
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = SessionForm()
    
    sessions = Session.objects.all().order_by('date', 'time').reverse()
    students = Student.objects.count()
    all_students = Student.objects.all()
    now = datetime.now().date()
    today_sessions_count = Session.objects.filter(date=now).count()
    context = {
        'sessions': sessions,
        'students': students,
        'today_sessions': today_sessions_count,
        'all_students': all_students,
    }
    return render(request, 'dashboard.html', {'form': form, 'context': context})

def login(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')
        user = authenticate(request, username=name, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Name or password invalid.')

    return render(request, 'authentication/sign-in.html')

def register_users(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                birth_date=form.cleaned_data['birth_date'],
                gender=form.cleaned_data['gender'],
                phone=form.cleaned_data['phone']
            )
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()

            return redirect('register_users')


def logout_view(request):
    logout(request)
    return redirect('login')

def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    session.delete()
    return redirect('index')

def register_professor_aee(request):
    if request.method == 'POST':
        form = ProfessorAEERegistrationForm(request.POST)
        if form.is_valid():
            user_form = UserForm({
                'name': form.cleaned_data['name'],
                'email': form.cleaned_data['email'],
                'birth_date': form.cleaned_data['birth_date'],
                'gender': form.cleaned_data['gender'],
                'phone': form.cleaned_data['phone'],
                'password': form.cleaned_data['password']
            })
            if user_form.is_valid():
                user = user_form.save()                
                ProfessorAEE.objects.create(
                    user=user,
                    specialty=form.cleaned_data['specialty']
                )
                messages.success(request, 'Professor AEE registered successfully!')
                return redirect('index')
            else:
                form.add_error(None, 'There was an error registering the user.')
    else:
        form = ProfessorAEERegistrationForm()
    
    return render(request, 'register_professor_aee.html', {'form': form})

def login_professor_aee(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Email or password invalid.')

    return render(request, 'authentication/login_professor_aee.html')
    return render(request, 'authentication/sign-up.html', {'form': form})
