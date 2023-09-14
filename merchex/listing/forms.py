from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Ticket


class SignUpForm(UserCreationForm):
    # Vous pouvez ajouter des champs personnalisés si nécessaire
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        
class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']
        
        # Personnalisation de l'étiquette du champ 'title'
        title = forms.CharField(label='Titre du ticket')