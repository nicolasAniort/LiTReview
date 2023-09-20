import django.urls
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from listing.forms import SignUpForm, ReviewForm, TicketForm
from .models import Ticket, Review
from listing import views


# CONNEXION / INSCRIPTION / DECONNEXION
# creation de la vue accueil
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


# creation de la vue inscription
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


#creation de la vue aprés connexion
@login_required
def flux(request):
    return render(request, 'flux.html')


#TICKET
# creation de la vue de creation d'un ticket simple 
@login_required
def create_ticket(request):
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        if ticket_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user  # Associez le ticket à l'utilisateur actuellement connecté
            ticket.save()
            if django.urls.re_path(r"^app/creation-ticket/", views.create_ticket, name='creation-ticket'):
                return redirect('flux')     
        """ Redirigez vers la page de app/flux après avoir créé le ticket sinon rester sur la page 
            app/nouvelle-critique/ 
        """
    # Si la méthode de la requête n'est pas POST ou si le formulaire n'est pas valide, continuez ici.
    ticket_form = TicketForm()
    
    return render(request, 'creation-ticket.html', {'ticket_form': ticket_form})

@login_required
def modify_ticket(request, ticked_id):
    #ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
        #if request.method == 'POST':
            # Gérez ici la logique de modification du ticket en fonction des données du formulaire
            # Après la modification, redirigez l'utilisateur vers la page de détails du ticket ou une autre page appropriée
            # ...
    return render(request, 'modify_ticket.html', {'ticket': ticket})


@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    if request.method == 'POST':
        # Gérez ici la logique de suppression du ticket
        ticket.delete()
        return redirect('mes-posts')  # Redirigez l'utilisateur vers la liste de ses tickets après la suppression

    return render(request, 'delete_ticket.html', {'ticket': ticket})


#POSTS
#creation de la vue de mes posts
@login_required
def my_posts(request):
    # Récupérer les tickets de l'utilisateur actuellement connecté
    tickets = Ticket.objects.filter(user=request.user)
    print(tickets)
    return render(request, 'mes-posts.html', {'tickets': tickets})


#CRITIQUE
# creation de la vue de creation d'une critique simple    
@login_required
def create_review(request):
    # Initialisation du formulaire de ticket
    ticket_form = TicketForm()
    
    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            # Créez une instance de Review et enregistrez-la dans la base de données
            review = Review(
                title=review_form.cleaned_data['title'],
                rating=review_form.cleaned_data['rating'],
                comment=review_form.cleaned_data['comment'],
                # Vous devrez ajouter d'autres champs en fonction de votre modèle
            )
            review.save()
            return redirect('flux')  # Redirigez l'utilisateur vers le flux
    else:
        review_form = ReviewForm()

    return render(request, 'nouvelle-critique.html', {'review_form': review_form, 'ticket_form': ticket_form})

# creation de la vue combine critique et ticket
@login_required
def create_combined(request):
    print(request)
    print("coucou")
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)
        if ticket_form.is_valid() and review_form.is_valid():
            # Traitez les données des deux formulaires comme vous le souhaitez
            ticket_data = ticket_form.cleaned_data
            review_data = review_form.cleaned_data

            return redirect('flux')  # Redirigez l'utilisateur vers le flux

    else:
        ticket_form = TicketForm()
        review_form = ReviewForm()

    return render(request, 'nouvelle-critique.html', {'ticket_form': ticket_form, 'review_form': review_form})


@login_required
def review_response(request):
    return render(request, 'reponse-critique.html')

@login_required
def subscription(request):
   return render(request, 'resultat-recherche.html') 
    

@login_required
def modify_review(request):
    return render(request, 'modifier-critique.html')


    return render(request, 'modifier-ticket.html')

"""def delete_review(request):
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