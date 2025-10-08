from django.shortcuts import get_object_or_404, render, redirect
from .models import Session
import json

def index(request):
    sessions = Session.objects.all()
    return render(request, 'dashboard.html', {'sessions': sessions})