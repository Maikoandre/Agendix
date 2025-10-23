from django import forms
from .models import Session, User

allowed_times = [
    ("07:30-08:30", "08:30 - 09:30"),
    ("09:00-10:30", "10:30 - 11:30"),
    ("13:30-14:30", "14:30 - 15:30"),
    ("15:30-16:30", "16:30 - 17:30"),
    ("19:30-20:30", "20:30 - 21:30"),
    ("21:30-22:30", "22:30 - 23:30"),
]


class SessionForm(forms.ModelForm):
    time = forms.ChoiceField(
        choices=allowed_times,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Hora",
        required=True
    )

    class Meta:
        model = Session
        fields = ['students', 'date', 'time', 'place', 'notes']
        widgets = {
            'students': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'place': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Local da sessão'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Notas sobre a sessão'}),
        }

    def save(self, commit=True):
        session = super().save(commit=False)
        if commit:
            session.save()
            self.save_m2m()
        return session


class UserForm(forms.ModelForm):
    class Meta():
        model = User
        fields = ['name', 'birth_date', 'email', 'gender', 'birth_place', 'password']
        name = forms.CharField(max_length=150)
        email = forms.EmailField()
        birth_date = forms.DateField()
        gender = forms.CharField(max_length=1)
        birth_place = forms.CharField(max_length=100)
        phone = forms.CharField(max_length=15)
        password =forms.CharField(max_length=128)