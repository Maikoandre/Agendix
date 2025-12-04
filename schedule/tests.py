from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Student

User = get_user_model()

class StudentListTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', password='password', name='Admin User')
        self.client.login(username='admin', password='password')
        
        self.user = User.objects.create_user(username='testuser', password='password', name='Test User')
        self.student = Student.objects.create(user=self.user, enrollment_number='12345')

    def test_student_list_view(self):
        response = self.client.get(reverse('student_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students/student_list.html')
        self.assertContains(response, 'Test User')
        self.assertContains(response, '12345')

    def test_delete_student(self):
        response = self.client.post(reverse('delete_student', args=[self.student.id]))
        self.assertRedirects(response, reverse('student_list'))
        self.assertFalse(Student.objects.filter(id=self.student.id).exists())
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_create_student(self):
        response = self.client.post(reverse('create_student'), {
            'name': 'New Student',
            'email': 'newstudent@example.com',
            'birth_date': '2000-01-01',
            'gender': 'M',
            'birth_place': 'City',
            'phone': '123456789',
            'password': 'password123',
            'password_confirm': 'password123',
            'enrollment_number': '54321',
            'parent': 'Parent Name',
            'course': 'Course Name'
        })
        self.assertRedirects(response, reverse('student_list'))
        self.assertTrue(Student.objects.filter(enrollment_number='54321').exists())
        self.assertTrue(User.objects.filter(email='newstudent@example.com').exists())
