import os
import django
import random
from datetime import date, timedelta
from faker import Faker

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aee.settings')
django.setup()

from schedule.models import (
    User, Student, Professor, ProfessorAEE, Session,
    SessionAttendance, Review, Report, PedagogicalProposal, Plan
)

fake = Faker('pt_BR')

def clean_database():
    """ Limpa o banco para evitar duplicatas e dados misturados. """
    print("Limpando banco de dados...")
    User.objects.all().delete()
    Session.objects.all().delete()
    Review.objects.all().delete()
    PedagogicalProposal.objects.all().delete()
    print("Banco de dados limpo.")

def create_users_students(num_students):
    students_list = []
    print(f"Criando {num_students} estudantes...")
    for _ in range(num_students):
        try:
            user_name = fake.user_name()
            user = User(
                username=user_name,
                name=fake.name(),
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=30),
                email=fake.unique.email(),
                gender=random.choice(['Masculino', 'Feminino', 'Outro']),
                birth_place=fake.city(),
                phone=fake.phone_number()
            )
            user.set_password('senha123')
            user.save()

            student = Student.objects.create(
                user=user,
                enrollment_number=fake.unique.random_number(digits=8, fix_len=True),
                parent=fake.name(),
                course=random.choice(['Engenharia de Software', 'Ciência da Computação', 'Sistemas de Informação', 'Análise e Dev. de Sistemas'])
            )
            students_list.append(student)
        except Exception:
            pass 
    return students_list

def create_users_professors(num_profs):
    profs_aee_list = []
    print(f"Criando {num_profs} professores...")
    for _ in range(num_profs):
        try:
            user_name = fake.user_name()
            user = User(
                username=user_name,
                name=fake.name(),
                birth_date=fake.date_of_birth(minimum_age=30, maximum_age=65),
                email=fake.unique.email(),
                gender=random.choice(['Masculino', 'Feminino']),
                birth_place=fake.city(),
                phone=fake.phone_number()
            )
            user.set_password('prof123')
            user.save()

            prof = Professor.objects.create(
                user=user,
                siape=fake.unique.random_number(digits=7, fix_len=True)
            )

            prof_aee = ProfessorAEE.objects.create(
                professor=prof,
                speciality=random.choice(['Deficiência Visual', 'TEA', 'Surdez', 'Altas Habilidades'])
            )
            profs_aee_list.append(prof_aee)
        except Exception:
            pass
    return profs_aee_list

def create_sessions_and_attendance(students_list):
    """ Gera sessões distribuídas nos últimos 12 meses para popular o gráfico. """
    print("Gerando histórico de sessões (últimos 12 meses)...")
    
    today = date.today()
    total_sessions = 0

    # Loop para os últimos 12 meses (incluindo o atual)
    for i in range(12):
        # Data de referência para o mês 'i' atrás
        month_reference = today - timedelta(days=30 * i)
        year = month_reference.year
        month = month_reference.month
        
        # Define aleatoriamente quantas sessões ocorreram neste mês (ex: 10 a 35)
        # A variação cria o efeito de "montanha" no gráfico
        num_sessions_in_month = random.randint(10, 35)

        for _ in range(num_sessions_in_month):
            # Escolhe um dia aleatório (1 a 28 para evitar erros de fim de mês)
            day = random.randint(1, 28)
            session_date = date(year, month, day)

            # Não cria sessões no futuro
            if session_date > today:
                continue

            session = Session.objects.create(
                date=session_date,
                time=f"{random.randint(8, 17)}:00",
                place=f"Sala {random.randint(1, 5)}",
                notes=fake.sentence()
            )

            # Associa um aluno aleatório
            if students_list:
                student = random.choice(students_list)
                SessionAttendance.objects.create(
                    session=session,
                    student=student,
                    present=random.choice([True, True, True, False]) # 75% de presença
                )
            total_sessions += 1

    print(f"Total de {total_sessions} sessões criadas ao longo do ano.")

def create_proposals_reviews_reports_plans(students_list, profs_aee_list):
    if not profs_aee_list: return

    print("Criando documentos (Planos, Relatórios)...")
    for student in students_list:
        prof_aee = random.choice(profs_aee_list)

        proposal = PedagogicalProposal.objects.create(
            objectives=fake.sentence(),
            methodologies=fake.sentence(),
            notes=fake.sentence()
        )

        review = Review.objects.create(
            field=random.choice(['Cognitivo', 'Social', 'Comunicação']),
            performance=random.choice(['Abaixo', 'Médio', 'Acima']),
            notes=fake.sentence()
        )

        report = Report.objects.create(
            title=f"Relatório - {student.user.name}",
            generated_date=date.today(),
            summary=fake.paragraph(),
            notes=fake.paragraph(),
            student=student,
            professor=prof_aee
        )
        report.reviews.add(review)

        Plan.objects.create(
            date=date.today() - timedelta(days=random.randint(1, 60)),
            recommendations=fake.text(),
            activities=fake.text(),
            resources=fake.text(),
            student=student,
            professor=prof_aee,
            pedagogical_proposal=proposal
        )

if __name__ == '__main__':
    # Recomendado: Limpar o banco para ver o efeito limpo no gráfico
    clean_database()
    
    # Aumentei a quantidade para o sistema parecer vivo
    NUM_ESTUDANTES = 50 
    NUM_PROFESSORES_AEE = 5
    
    students = create_users_students(NUM_ESTUDANTES)
    professors = create_users_professors(NUM_PROFESSORES_AEE)
    
    if students and professors:
        # Não passamos mais num_sessions fixo, o script calcula por mês
        create_sessions_and_attendance(students)
        create_proposals_reviews_reports_plans(students, professors)
        print("\n--- Povoamento Completo! ---")
    else:
        print("\n--- Erro: Faltam estudantes ou professores. ---")