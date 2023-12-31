from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm


# creation de la vue hello.
def hello(request):
    # affichage du texte
    return HttpResponse("Hello Django !")
def home(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)  # Créez une instance du formulaire
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('flux')  # Redirigez vers le flux de l'utilisateur
            else:
                # Gérer une connexion invalide
                pass
    else:
        form = AuthenticationForm(request)  # Créez une instance du formulaire vide

    return render(request, 'accueil.html', {'form': form})  # Passez le formulaire dans le contexte

def registration(request):
    return render(request, 'listing/inscription.html')
def flux(request):
    return render(request, 'listing/flux.html')
def subscription(request):
    return render(request, 'listing/abonnement.html')
def create_ticket(request):
    return render(request, 'listing/creation-ticket.html')
def new_review(request):
    return render(request, 'listing/nouvelle-critique.html')
def critic_response(request):
    return render(request, 'listing/reponse-critique.html')
def my_posts(request):
    return render(request, 'listing/mes-posts.html')
def modify_review(request):
    return render(request, 'listing/modifier-critique.html')
def modify_ticket(request):
    return render(request, 'listing/modifier-ticket.html')
"""def delete_ticket(request):
    return render(request, 'listing/supprimer-ticket.html')
def delete_review(request):
    return render(request, 'listing/supprimer-critique.html')   
def delete_account(request):
    return render(request, 'listing/supprimer-compte.html')
def modify_account(request):
    return render(request, 'listing/modifier-compte.html')  
def login(request):
    return render(request, 'listing/connexion.html')
def logout(request):
    return render(request, 'listing/deconnexion.html')
def ticket(request):
    return render(request, 'listing/ticket.html')
def review(request):
    return render(request, 'listing/critique.html')
def account(request):
    return render(request, 'listing/compte.html')
def search(request):
    return render(request, 'listing/recherche.html')
def search_result(request):
    return render(request, 'listing/resultat-recherche.html')
"""