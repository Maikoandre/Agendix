from django.shortcuts import get_object_or_404, render, redirect
from .models import Session, User, Student
from .forms import SessionForm, UserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, date

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
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Name or password invalid.')
    
    return render(request, 'authentication/sign-in.html')

def register_users(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            User.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                birth_date=form.cleaned_data['birth_date'],
                gender=form.cleaned_data['gender'],
                phone=form.cleaned_data['phone'],
                password=form.cleaned_data['password']
                
            )
            return redirect('register_users')
    else:
        form = UserForm()
        
    return render(request, 'authentication/sign-up.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    session.delete()
    return redirect('index')