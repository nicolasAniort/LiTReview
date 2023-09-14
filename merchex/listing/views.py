from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from listing.forms import SignUpForm, TicketForm



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
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('flux')  # Redirigez vers la page de votre choix après l'inscription
    else:
        form = SignUpForm()
    return render(request, 'inscription.html', {'form': form})

#vue aprés connexion
@login_required
def flux(request):
    return render(request, 'flux.html')

@login_required
def subscription(request):
    return render(request, 'abonnement.html')

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user  # Associez le ticket à l'utilisateur actuellement connecté
            ticket.save()
            return redirect('flux')  # Redirigez vers la page de flux après avoir créé le ticket
    else:
        form = TicketForm()
    
    return render(request, 'creation-ticket.html', {'form': form})

@login_required
def new_review(request):
    return render(request, 'nouvelle-critique.html')

@login_required
def critic_response(request):
    return render(request, 'reponse-critique.html')

@login_required
def my_posts(request):
    return render(request, 'mes-posts.html')

@login_required
def modify_review(request):
    return render(request, 'modifier-critique.html')

@login_required
def modify_ticket(request):
    return render(request, 'modifier-ticket.html')
"""def delete_ticket(request):
    return render(request, 'supprimer-ticket.html')
def delete_review(request):
    return render(request, 'supprimer-critique.html')   
def delete_account(request):
    return render(request, 'supprimer-compte.html')
def modify_account(request):
    return render(request, 'modifier-compte.html')  
def login(request):
    return render(request, 'connexion.html')
def logout(request):
    return render(request, 'deconnexion.html')
def ticket(request):
    return render(request, 'ticket.html')
def review(request):
    return render(request, 'critique.html')
def account(request):
    return render(request, 'compte.html')
def search(request):
    return render(request, 'recherche.html')
def search_result(request):
    return render(request, 'resultat-recherche.html')
"""