try:
    from django.urls import path
except Exception:
    def path(route, view, kwargs=None, name=None):
        return (route, view, kwargs, name)

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_users, name='register_users'),
    path('delete_session/<int:session_id>', views.delete_session, name='delete_session'),
    path('student/profile/<int:pk>/details/', views.profile_view, name='profile_view'),
    path('students/', views.student_list, name='student_list'),
    path('student/<int:pk>/delete/', views.delete_student, name='delete_student'),
    path('students/create/', views.create_student, name='create_student'),
]