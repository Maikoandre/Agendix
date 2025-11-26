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
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

# Importações Locais (Local App)
from .forms import ProfessorAEERegistrationForm, SessionForm, UserForm
from .models import Professor, ProfessorAEE, Session, Student, User

#@login_required(login_url='login')
def index(request):
    # Lógica do Formulário (POST) - Mantém igual
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = SessionForm()
    
    now = timezone.localdate()
    
    # --- LÓGICA DE FILTRO E PESQUISA ---
    search_query = request.GET.get('q', '') # Pega o termo da busca da URL (?q=nome)
    
    # Começa com todas as sessões ordenadas
    sessions_list = Session.objects.all().order_by('date', 'time').reverse()
    
    # Se houver busca, filtra por nome do estudante OU local OU notas
    if search_query:
        sessions_list = sessions_list.filter(
            Q(students__user__name__icontains=search_query) | 
            Q(place__icontains=search_query) |
            Q(notes__icontains=search_query)
        ).distinct()

    # --- PAGINAÇÃO ---
    paginator = Paginator(sessions_list, 5) # Mostra 5 itens por página (ajuste como quiser)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- GRÁFICO (Mantém sua lógica existente) ---
    sessions_per_month = Session.objects.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    chart_months = [entry['month'].strftime('%b') for entry in sessions_per_month]
    chart_counts = [entry['count'] for entry in sessions_per_month]
    
    # --- CONTEXTO ---
    context = {
        'sessions': page_obj, # Agora passamos o objeto paginado, não a lista toda!
        'students': Student.objects.count(),
        'today_sessions': Session.objects.filter(date=now).count(),
        'chart_months': chart_months,
        'chart_counts': chart_counts,
        'search_query': search_query, # Devolvemos a busca para manter no input
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
            # Extrair dados limpos
            data = form.cleaned_data
            
            # 1. Criar o Usuário Base
            # Nota: create_user lida com o hash da senha automaticamente
            try:
                with transaction.atomic(): # Garante que ou cria tudo ou não cria nada
                    user = User.objects.create(
                        name=data['name'],
                        email=data['email'],
                        birth_date=data['birth_date'],
                        gender=data['gender'],
                        birth_place=data['birth_place'],
                        phone=data['phone']
                    )
                    user.set_password(data['password'])
                    user.save()

                    # 2. Criar o Professor vinculado ao Usuário
                    professor = Professor.objects.create(
                        user=user,
                        siape=data['siape']
                    )

                    # 3. Criar o Professor AEE vinculado ao Professor
                    ProfessorAEE.objects.create(
                        professor=professor,
                        speciality=data['speciality']
                    )

                    # Logar o usuário imediatamente
                    auth_login(request, user)
                    return redirect('index')

            except Exception as e:
                # Se der erro (ex: email duplicado), mostra mensagem
                messages.error(request, f"Erro ao cadastrar: {e}")
                
    else:
        form = ProfessorAEERegistrationForm()
    
    return render(request, 'authentication/professoraee-sign-in.html', {'form': form})

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


def profile_view(request, pk):
    student_obj = get_object_or_404(Student, pk=pk)
    return render(request, 'students/profile.html', {'student': student_obj})