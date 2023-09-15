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
        labels = {
            'title': 'Titre du ticket',  # Personnalisation de l'étiquette du champ 'title'
        }
    
class ReviewForm(forms.Form):
    title = forms.CharField(label='Titre de la critique')
    RATING_CHOICES = [(str(i), i) for i in range(6)]
    rating = forms.ChoiceField(
        label='Note',
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
    )
    comment = forms.CharField(label='Commentaire', widget=forms.Textarea)
    
class CombinedForm(forms.Form):#formulaire combiné de TicketForm et ReviewForm
    ticket_form = TicketForm()
    review_form = ReviewForm()    