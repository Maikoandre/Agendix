from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    name = models.CharField(max_length=150, unique=True)
    birth_date = models.DateField()
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10)
    birth_place = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=128)

    def set_password(self, password):
        self.password = make_password(password)

    def check_password(self, password):
        return check_password(password, self.password)

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enrollment_number = models.CharField(max_length=20, unique=True)
    parent = models.CharField(max_length=150, null=True, blank=True)
    course = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f"{self.user.name} - {self.enrollment_number}"

class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    siape = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.user.name} - {self.siape}"

class ProfessorAEE(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name="aees")
    speciality = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.professor.user.name} - {self.speciality}"

class Session(models.Model):
    date = models.DateField()
    time = models.CharField(null=True, blank=True)
    place = models.CharField(max_length=150, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    students = models.ManyToManyField(Student, through='SessionAttendance', related_name="sessions")

    def __str__(self):
        return f"Session on {self.date} at {self.place}"

class SessionAttendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    present = models.BooleanField(default=False)

    class Meta:
        unique_together = ("session", "student")

class Review(models.Model):
    field = models.CharField(max_length=150)
    performance = models.CharField(max_length=150)
    notes = models.TextField()

    def __str__(self):
        return f"Review: {self.field} - {self.performance}"

class Report(models.Model):
    title = models.CharField(max_length=150)
    generated_date = models.DateField()
    summary = models.TextField()
    notes = models.TextField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="reports")
    professor = models.ForeignKey(ProfessorAEE, on_delete=models.CASCADE, related_name="reports")
    reviews = models.ManyToManyField(Review, related_name="reports")

    def __str__(self):
        return f"{self.title} for {self.student.user.name}"

class PedagogicalProposal(models.Model):
    objectives = models.TextField()
    methodologies = models.TextField()
    notes = models.TextField()

    def __str__(self):
        return f"Proposal: {self.objectives[:30]}..."

class Plan(models.Model):
    date = models.DateField()
    recommendations = models.TextField()
    activities = models.TextField()
    resources = models.TextField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="plans")
    professor = models.ForeignKey(ProfessorAEE, on_delete=models.CASCADE, related_name="plans")
    pedagogical_proposal = models.ForeignKey(PedagogicalProposal, on_delete=models.CASCADE, related_name="plans")

    class Meta:
        unique_together = ("date", "student")

    def __str__(self):
        return f"Plan for {self.student.user.name} on {self.date}"
