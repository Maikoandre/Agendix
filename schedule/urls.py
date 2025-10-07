try:
    from django.urls import path
except Exception:
    def path(route, view, kwargs=None, name=None):
        return (route, view, kwargs, name)

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register', views.register_users, name='register_users'),
    path('delete_session/<int:session_id>', views.delete_session, name='delete_session'),
    path("register/professoraee", views.register_professor_aee, name='register_professor_aee'),
    path('login/professor/', views.login_professor_aee, name='login_professor_aee'),
    path('student/profile/<int:pk>/details/', views.profile_view, name='student_detail'),
]