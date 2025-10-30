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

@transaction.atomic  # Garante que ou tudo salva, ou nada salva
def professorAEE_register(request):
    if request.method == "POST":
        form = ProfessorAEERegistrationForm(request.POST)
        if form.is_valid():
            try:
                # 1. Criar o User
                new_user = User(
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    birth_date=form.cleaned_data['birth_date'],
                    gender=form.cleaned_data['gender'],
                    birth_place=form.cleaned_data['birth_place'],
                    phone=form.cleaned_data['phone']
                )
                # Usa o método set_password (do seu model) para hashear a senha
                new_user.set_password(form.cleaned_data['password'])
                new_user.save()

                # 2. Criar o Professor, linkando ao User
                new_professor = Professor.objects.create(
                    user=new_user,
                    siape=form.cleaned_data['siape']
                )

                # 3. Criar o ProfessorAEE, linkando ao Professor
                ProfessorAEE.objects.create(
                    professor=new_professor,
                    speciality=form.cleaned_data['speciality']
                )

                # Use 'messages' se quiser notificar o sucesso
                # messages.success(request, 'Professor AEE registrado com sucesso!')
                return redirect('professorAEE_register') # Redireciona para limpar o form

            except Exception as e:
                # Se algo der errado (ex: email ou nome duplicado)
                # Você pode adicionar uma mensagem de erro aqui
                # messages.error(request, f'Erro ao registrar: {e}')
                pass # Deixa o form ser re-exibido com os erros
    
    else:
        form = ProfessorAEERegistrationForm()

    # Você precisará criar este template
    return render(request, 'authentication/professoraee-sign-up.html', {'form': form})

def professorAEE_login(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')
        
        # 1. Autentica o 'User' normalmente
        user = authenticate(request, username=name, password=password)
        
        if user is not None:
            # 2. Verifica se o User é um Professor AEE
            try:
                # Checa se o 'user' tem um 'professor'
                # e se esse 'professor' tem um 'aee' relacionado
                is_professor_aee = ProfessorAEE.objects.filter(professor__user=user).exists()
                
                if is_professor_aee:
                    # 3. Se for, faz o login e redireciona
                    login(request, user)
                    return redirect('index') # Redireciona para o dashboard
                else:
                    # 4. Se não for Professor AEE, exibe erro
                    messages.error(request, 'Este usuário não é um Professor AEE.')
                    
            except Professor.DoesNotExist:
                # Caso o 'user' não tenha um 'professor' (é aluno ou outro tipo)
                messages.error(request, 'Este usuário não é um Professor AEE.')
        else:
            # Erro de nome ou senha inválida (da view original)
            messages.error(request, 'Nome ou senha inválida.')
    
    # Renderiza a mesma tela de login (você pode criar uma específica se quiser)
    return render(request, 'authentication/sign-in.html')