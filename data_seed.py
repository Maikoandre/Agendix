import os
import django
import random
from datetime import date, timedelta
from faker import Faker

# 1. AJUSTE: Mude 'seu_projeto.settings' para o nome do seu arquivo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aee.settings')
django.setup()

# 2. AJUSTE: Mude 'sua_app' para o nome do app onde seus models estão
from schedule.models import (
    User, Student, Professor, ProfessorAEE, Session,
    SessionAttendance, Review, Report, PedagogicalProposal, Plan
)

fake = Faker('pt_BR')

def clean_database():
    """ Limpa os dados dos modelos para evitar duplicatas. """
    print("Limpando banco de dados...")
    # A limpeza do User cascateia para Student, Professor, etc.
    User.objects.all().delete()
    # Limpa modelos que não têm relação direta com User
    Session.objects.all().delete()
    Review.objects.all().delete()
    PedagogicalProposal.objects.all().delete()
    print("Banco de dados limpo.")

def create_users_students(num_students):
    """ Cria usuários base e estudantes. """
    students_list = []
    for _ in range(num_students):
        try:
            user = User(
                name=fake.name(),
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=30),
                email=fake.unique.email(),
                gender=random.choice(['Masculino', 'Feminino', 'Outro']),
                birth_place=fake.city(),
                phone=fake.phone_number()
            )
            # Usa o método do model para hashear a senha
            user.set_password('senha123')
            user.save()

            student = Student.objects.create(
                user=user,
                enrollment_number=fake.unique.random_number(digits=8, fix_len=True),
                parent=fake.name(),
                course=random.choice(['Engenharia de Software', 'Ciência da Computação', 'Sistemas de Informação', 'Análise e Dev. de Sistemas'])
            )
            students_list.append(student)
        except Exception as e:
            print(f"Erro ao criar estudante (email/nome duplicado?): {e}")

    print(f"{len(students_list)} estudantes criados.")
    return students_list

def create_users_professors(num_profs):
    """ Cria usuários base, professores e professores AEE. """
    profs_aee_list = []
    for _ in range(num_profs):
        try:
            user = User(
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

            # Cria a especialização AEE para o professor
            prof_aee = ProfessorAEE.objects.create(
                professor=prof,
                speciality=random.choice(['Deficiência Visual', 'Transtorno do Espectro Autista', 'Surdez', 'Altas Habilidades'])
            )
            profs_aee_list.append(prof_aee)
        except Exception as e:
            print(f"Erro ao criar professor (email/nome duplicado?): {e}")

    print(f"{len(profs_aee_list)} professores AEE criados.")
    return profs_aee_list

def create_sessions_and_attendance(students_list, num_sessions=10):
    """ Cria sessões e registra a presença de um único aluno por sessão. """
    print("Criando sessões...")
    for _ in range(num_sessions):
        session = Session.objects.create(
            date=fake.date_between(start_date='-6m', end_date='-1d'),
            time=f"{random.randint(8, 17)}:00",
            place=f"Sala de Recursos {random.randint(1, 5)}",
            notes=fake.paragraph(nb_sentences=2)
        )

        # Seleciona apenas 1 aluno aleatório para esta sessão (se houver ao menos 1)
        if students_list:
            student = random.choice(students_list)
            SessionAttendance.objects.create(
                session=session,
                student=student,
                present=random.choice([True, False, True])  # Mais chance de estar presente
            )
    
    # Create a session for today
    session = Session.objects.create(
        date=date.today(),
        time=f"{random.randint(8, 17)}:00",
        place=f"Sala de Recursos {random.randint(1, 5)}",
        notes="Sessão de hoje."
    )
    if students_list:
        student = random.choice(students_list)
        SessionAttendance.objects.create(
            session=session,
            student=student,
            present=True
        )

    print(f"{num_sessions + 1} sessões criadas.")

def create_proposals_reviews_reports_plans(students_list, profs_aee_list):
    """ Cria os demais itens (Planos, Relatórios, etc.) para cada aluno. """
    if not profs_aee_list:
        print("Não há professores AEE para criar relatórios/planos.")
        return

    print("Criando planos, relatórios e propostas...")
    for student in students_list:
        # Associa um professor AEE aleatório ao aluno
        prof_aee = random.choice(profs_aee_list)

        # 1. Proposta Pedagógica
        proposal = PedagogicalProposal.objects.create(
            objectives=fake.sentence(nb_words=10),
            methodologies=fake.sentence(nb_words=10),
            notes=fake.paragraph(nb_sentences=1)
        )

        # 2. Avaliação (Review)
        review = Review.objects.create(
            field=random.choice(['Desenvolvimento Cognitivo', 'Interação Social', 'Comunicação']),
            performance=random.choice(['Abaixo do esperado', 'Dentro do esperado', 'Acima do esperado']),
            notes=fake.sentence()
        )

        # 3. Relatório (Report) - Associado ao Aluno, Prof AEE e Review
        report = Report.objects.create(
            title=f"Relatório Semestral - {student.user.name}",
            generated_date=date.today(),
            summary=fake.paragraph(nb_sentences=3),
            notes=fake.paragraph(nb_sentences=2),
            student=student,
            professor=prof_aee
        )
        report.reviews.add(review) # Adiciona a relação ManyToMany

        # 4. Plano (Plan) - Associado ao Aluno, Prof AEE e Proposta
        Plan.objects.create(
            date=date.today() - timedelta(days=random.randint(1, 30)),
            recommendations=fake.text(max_nb_chars=200),
            activities=fake.text(max_nb_chars=200),
            resources=fake.text(max_nb_chars=150),
            student=student,
            professor=prof_aee,
            pedagogical_proposal=proposal
        )
    print(f"Planos e Relatórios criados para {len(students_list)} alunos.")


# --- Execução Principal ---
if __name__ == '__main__':
    # Limpa o DB antes de popular
    #clean_database()
    
    # Define quantos de cada você quer criar
    NUM_ESTUDANTES = 25
    NUM_PROFESSORES_AEE = 5
    NUM_SESSOES = 10

    # Executa as funções de povoamento na ordem correta
    students = create_users_students(NUM_ESTUDANTES)
    professors = create_users_professors(NUM_PROFESSORES_AEE)
    
    if students and professors:
        create_sessions_and_attendance(students, NUM_SESSOES)
        create_proposals_reviews_reports_plans(students, professors)
        print("\n--- Povoamento concluído! ---")
    else:
        print("\n--- Povoamento falhou (Faltam estudantes ou professores). ---")
