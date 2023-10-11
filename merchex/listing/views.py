import django.urls
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from listing.forms import SignUpForm, ReviewForm, TicketForm
from .models import Ticket, Review, UserFollows
from listing import views
from itertools import chain
from django.db.models import CharField, Value
from .models import Subscription
from django.contrib.auth.models import User
from .forms import UserSearchForm


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

# FLUX 
#creation de la vue FLUX
@login_required
def flux(request):
    reviews = get_users_viewable_reviews(request)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))
    
    tickets = get_users_viewable_tickets(request)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )

    return render(request, 'flux.html', context={'posts': posts})

@login_required
def get_users_viewable_reviews(request):
    # Cette méthode récupère toutes les critiques visibles pour l'utilisateur
    # et les critiques en réponse à celles de ses abonnements.
    user = request.user
    # Récupérer toutes les critiques de l'utilisateur actuellement connecté
    reviews = Review.objects.filter(user=user, visibility=True)

    # Récupérer les utilisateurs suivis par l'utilisateur actuellement connecté
    followed_users = UserFollows.objects.filter(user=user).values_list('followed_user', flat=True)

    # Récupérer toutes les critiques des utilisateurs suivis
    reviews_by_followed_users = Review.objects.filter(user__in=followed_users, visibility=True)

    # Combiner les critiques de l'utilisateur et celles des utilisateurs suivis
    all_reviews = reviews | reviews_by_followed_users

    return all_reviews

@login_required
def get_users_viewable_tickets(request):
    # Cette méthode récupère tous les tickets visibles pour l'utilisateur
    # et les tickets en réponse à ceux de ses abonnements.
    user = request.user
    # Récupérer tous les tickets de l'utilisateur actuellement connecté
    tickets = Ticket.objects.filter(user=user, visibility=True)

    # Récupérer les utilisateurs suivis par l'utilisateur actuellement connecté
    followed_users = UserFollows.objects.filter(user=user).values_list('followed_user', flat=True)

    # Récupérer tous les tickets des utilisateurs suivis
    tickets_by_followed_users = Ticket.objects.filter(user__in=followed_users, visibility=True)

    # Combiner les tickets de l'utilisateur et ceux des utilisateurs suivis
    all_tickets = tickets | tickets_by_followed_users

    return all_tickets

    

# TICKET
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
def modify_ticket(request, ticket_id):
    # Récupérez le ticket à modifier
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)  # Pré-remplissez le formulaire avec les données du ticket

        if form.is_valid():
            form.save()  # Enregistrez les modifications si le formulaire est valide
            return redirect('mes-posts')  # Redirigez l'utilisateur vers la liste de ses tickets après la modification
    else:
        form = TicketForm(instance=ticket)  # Créez une instance du formulaire pré-rempli

    return render(request, 'modifier-ticket.html', {'ticket': ticket, 'form': form})


@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    print("**",ticket.id)  # Utilisez ticket.id pour obtenir l'ID du ticket

    if request.method == 'POST':
        # Gérez ici la logique de suppression du ticket
        ticket.delete()
        #mise a jour de la liste des tickets restants
        remaining_tickets = Ticket.objects.filter(user=request.user)
        return render(request, 'mes-posts.html', {'tickets': remaining_tickets})  # Redirigez l'utilisateur vers la liste de ses tickets après la suppression

    return render(request, 'mes-posts.html', {'ticket': ticket})


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


@login_required
def view_review(request, review_id):
    # Récupérez la critique en fonction de son ID, ou renvoyez une erreur 404 si elle n'existe pas
    review = get_object_or_404(Review, id=review_id)

    # Vous pouvez maintenant utiliser l'objet 'review' pour accéder aux données de la critique
    # Par exemple, review.title, review.rating, review.comment, etc.

    return render(request, 'nom_de_votre_template.html', {'review': review})

@login_required
def view_ticket(request, ticket_id):
    # Récupérez la critique en fonction de son ID, ou renvoyez une erreur 404 si elle n'existe pas
    ticket = get_object_or_404(Review, id=ticket_id)

    # Vous pouvez maintenant utiliser l'objet 'review' pour accéder aux données de la critique
    # Par exemple, review.title, review.rating, review.comment, etc.

    return render(request, 'nom_de_votre_template.html', {'review': ticket})

#Abonnement
@login_required
def available_users(request):
    # Récupérez tous les utilisateurs, à l'exception de l'utilisateur connecté
    users = User.objects.exclude(id=request.user.id)
    
    # Récupérez les utilisateurs déjà abonnés par l'utilisateur connecté
    subscriptions = Subscription.objects.filter(follower=request.user).values_list('following_id', flat=True)
    
    return render(request, 'available_users.html', {'users': users, 'subscriptions': subscriptions})

@login_required
def followers(request):
    # Récupérez les utilisateurs qui suivent l'utilisateur connecté
    followers = Subscription.objects.filter(following=request.user)
    
    return render(request, 'followers.html', {'followers': followers})

@login_required
def follow(request, user_id):
    # Créez une instance de Subscription pour suivre un utilisateur
    following_user = User.objects.get(id=user_id)
    subscription = Subscription(follower=request.user, following=following_user)
    subscription.save()
    
    return redirect('available_users')

@login_required
def unfollow(request, user_id):
    # Supprimez une instance de Subscription pour cesser de suivre un utilisateur
    following_user = User.objects.get(id=user_id)
    Subscription.objects.filter(follower=request.user, following=following_user).delete()
    
    return redirect('available_users')

def subscription(request):
    user_search_form = UserSearchForm()
    # Obtenez la liste des utilisateurs que l'utilisateur connecté suit déjà
    following_users = Subscription.objects.filter(user=request.user).values_list('searched_user', flat=True)
    # Obtenez la liste des utilisateurs qui suivent l'utilisateur connecté
    followers = Subscription.objects.filter(searched_user=request.user)

    if request.method == 'POST':
        # Traitez le formulaire de recherche d'utilisateur
        user_search_form = UserSearchForm(request.POST)
        if user_search_form.is_valid():
            # Récupérez l'utilisateur recherché à partir du formulaire
            searched_user = user_search_form.cleaned_data['searched_query']

            # Créez une instance de Subscription pour l'abonnement
            subscription = Subscription(user=request.user, searched_user=searched_user)
            subscription.save()

    return render(request, 'available_users.html', {'user_search_form': user_search_form, 'following_users': following_users, 'followers': followers})

