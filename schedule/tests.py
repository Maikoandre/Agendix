from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Student

User = get_user_model()

class StudentListTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password', name='Test User')
        self.student = Student.objects.create(user=self.user, enrollment_number='12345')
        self.client.login(username='testuser', password='password')

    def test_student_list_view(self):
        response = self.client.get(reverse('student_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students/student_list.html')
        self.assertContains(response, 'Test User')
        self.assertContains(response, '12345')
