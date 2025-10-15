from django.shortcuts import get_object_or_404, render, redirect
from .models import Session
from .forms import SessionForm

def index(request):
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = SessionForm()
    
    sessions = Session.objects.all()
    return render(request, 'dashboard.html', {'form': form, 'sessions': sessions})