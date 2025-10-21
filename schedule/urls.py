from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('register', views.register_users, name='register_users'),
    path('delete_session/<int:session_id>', views.delete_session, name='delete_session')
]