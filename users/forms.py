from django import forms
from .models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password_hash', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']
        widgets = {
            'password_hash': forms.PasswordInput(),
        }
