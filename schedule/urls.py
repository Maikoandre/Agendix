try:
    from django.urls import path
except Exception:
    # Fallback for environments where Django isn't installed or the editor can't resolve django.
    # This minimal shim allows the module to be imported (useful for linters or editors).
    def path(route, view, kwargs=None, name=None):
        return (route, view, kwargs, name)

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register', views.register_users, name='register_users'),
    path('delete_session/<int:session_id>', views.delete_session, name='delete_session'),
    path("register/professoraee", views.professorAEE_register, name='professorAEE_register'),
    path('login/professor/', views.professorAEE_login, name='professorAEE_login'),
]