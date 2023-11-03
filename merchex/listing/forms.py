from django import forms
from django.conf import settings
from django.core.files.base import ContentFile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Ticket, Subscription, Review
import os


# Formulaire d'inscription pour les utilisateurs
class SignUpForm(UserCreationForm):
    # SignUpForm est un formulaire d'inscription pour les utilisateurs.
    # Il hérite de UserCreationForm, qui fournit des champs de base tels 
    # que username, password1, et password2.
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]


# Formulaire pour créer un nouveau ticket
class TicketForm(forms.ModelForm):
    # TicketForm est un formulaire pour créer un nouveau ticket.
    # Il est basé sur le modèle Ticket et inclut les champs 
    # title, description, et image.
    class Meta:
        model = Ticket
        fields = ["title", "description", "image"]
        labels = {
            "title": "Titre du ticket",  # Personnalisation de l'étiquette 
            #du champ 'title'
        }

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image")
        if not image:
            # Si l'utilisateur n'a pas fourni d'image, ajoutez une image par défaut.
            default_image_path = None
            if settings.STATIC_ROOT:
                default_image_path = os.path.join(settings.STATIC_ROOT, "default", "default_ticket_image.png")
                print("default_image_path: ", default_image_path)
            if default_image_path and os.path.exists(default_image_path):
                print("default image exists")
                with open(default_image_path, "rb") as f:
                    image_data = f.read()
                image = ContentFile(image_data, name="default_ticket_image.png")
                cleaned_data["image"] = image
        return cleaned_data
# Formulaire pour soumettre une critique


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(str(i), i) for i in range(6)]
    rating = forms.ChoiceField(
        label="Note",
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
    )
    headline = forms.CharField(label="Titre de la critique")
    body = forms.CharField(label="Commentaire", widget=forms.Textarea)

    class Meta:
        model = Review
        fields = ['headline', 'rating', 'body']
        labels = {
            'headline': 'Titre de la critique',
            'body': 'Commentaire',
        }
        widgets = {
            'body': forms.Textarea,
        }

# Formulaire combiné de TicketForm et ReviewForm
class CombinedForm(forms.Form):
    # CombinedForm est un formulaire qui combine à la fois 
    # TicketForm et ReviewForm.
    # Cela peut être utile si vous avez besoin de soumettre à la fois
    # un ticket et une critique en même temps.
    ticket_form = TicketForm()
    review_form = ReviewForm()


# Formulaire pour gérer les abonnements
class SubscriptionForm(forms.ModelForm):
    # SubscriptionForm est un formulaire pour gérer les abonnements.
    # Il est basé sur le modèle Subscription.
    class Meta:
        model = Subscription
        fields = []


# Formulaire de recherche d'utilisateurs
class UserSearchForm(forms.Form):
    search_query = forms.CharField(
        label='Recherche d\'utilisateur',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Commencez à taper le nom...'}),
        required=False
    )

    def search_users(self):
        query = self.cleaned_data.get("search_query")
        if query:
            # Effectuez la recherche d'utilisateurs en fonction du champ 'username'
            # Vous pouvez personnaliser cela pour rechercher d'autres champs si nécessaire
            return User.objects.filter(username__icontains=query)
        return User.objects.none()
