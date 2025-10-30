from django.shortcuts import get_object_or_404, render, redirect
from .models import Session, User, ProfessorAEE, Professor, Student
from .forms import SessionForm, UserForm, ProfessorAEERegistrationForm
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
from django.contrib.auth.hashers import make_password
from django.db import transaction

#@login_required(login_url='login')
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

@transaction.atomic 
def professorAEE_register(request):
    if request.method == "POST":
        form = ProfessorAEERegistrationForm(request.POST)
        if form.is_valid():
            try:
                new_user = User(
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    birth_date=form.cleaned_data['birth_date'],
                    gender=form.cleaned_data['gender'],
                    birth_place=form.cleaned_data['birth_place'],
                    phone=form.cleaned_data['phone']
                )
                new_user.set_password(form.cleaned_data['password'])
                new_user.save()

                new_professor = Professor.objects.create(
                    user=new_user,
                    siape=form.cleaned_data['siape']
                )

                ProfessorAEE.objects.create(
                    professor=new_professor,
                    speciality=form.cleaned_data['speciality']
                )

                return redirect('professorAEE_register')

            except Exception as e:
                messages.error(request, f'Erro ao registrar: {e}')
    
    else:
        form = ProfessorAEERegistrationForm()

    return render(request, 'authentication/professoraee-sign-up.html', {'form': form})

def professorAEE_login(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')
        
        user = authenticate(request, username=name, password=password)
        
        if user is not None:
            try:
                is_professor_aee = ProfessorAEE.objects.filter(professor__user=user).exists()
                
                if is_professor_aee:
                    login(request, user)
                    return redirect('index')
                else:
                    messages.error(request, 'Este usuário não é um Professor AEE.')
                    
            except Professor.DoesNotExist:
                messages.error(request, 'Este usuário não é um Professor AEE.')
        else:
            messages.error(request, 'Nome ou senha inválida.')
    
    return render(request, 'authentication/sign-in.html')