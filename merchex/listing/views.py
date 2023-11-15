from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from itertools import chain
from django.db import IntegrityError
from django.db.models import CharField, Value
from listing.forms import SignUpForm, ReviewForm, TicketForm, UserSearchForm
from .models import Ticket, Review, UserFollows, Subscription, User
from .forms import SubscriptionForm

# CONNEXION / INSCRIPTION / DECONNEXION
# Créez une instance du formulaire


def home(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        # Créez une instance du formulaire
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("flux")  # Redirigez vers le flux de l'utilisateur
            else:
                # Gérez une connexion invalide
                pass
    else:
        form = AuthenticationForm(request)  # Créez une instance du formulaire vide

    return render(request, "accueil.html", {"form": form})


"""Cette vue gère la connexion des utilisateurs. 
Elle vérifie si un utilisateur a soumis le formulaire de connexion
(méthode POST). Si le formulaire est valide,elle authentifie 
l'utilisateur et le redirige vers le flux. Si le formulaire est invalide,
elle peut gérer la connexion invalide (vous pouvez ajouter une logique
de gestion des erreurs ici)."""


# creation de la vue inscription
def registration(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(
                "flux"
            )  # Redirigez vers la page de votre choix après l'inscription
    else:
        form = SignUpForm()
    return render(request, "inscription.html", {"form": form})


"""Cette vue gère l'inscription des utilisateurs. Si un utilisateur soumet 
le formulaire d'inscription (méthode POST)et que le formulaire est valide, 
un nouvel utilisateur est créé et connecté, puis redirigé vers le flux."""


# FLUX
# creation de la vue FLUX


@login_required
def flux(request):
    reviews = get_users_viewable_reviews(request)
    reviews = reviews.annotate(content_type=Value("REVIEW", CharField()))
    tickets = get_users_viewable_tickets(request)
    tickets = tickets.annotate(content_type=Value("TICKET", CharField()))

    posts = sorted(
        # chain(reviews, tickets), key=lambda post: post.time_created, reverse=True
        chain(tickets),
        key=lambda post: post.time_created,
        reverse=True,
    )

    for post in posts:
        post.can_create_review = (
            post.user != request.user and not post.review_set.exists()
        )

    return render(request, "flux.html", context={"posts": posts})


"""Cette vue génère le flux d'activité de l'utilisateur. 
Elle récupère les critiques et les tickets visibles pour 
l'utilisateur en utilisant les fonctions 
get_users_viewable_reviews et get_users_viewable_tickets. Ensuite, 
elle combine ces deux types de publications dans une liste de 
"posts" triés par date de création,puis les affiche dans un modèle."""


@login_required
def get_users_viewable_reviews(request):
    # Cette méthode récupère toutes les critiques visibles pour l'utilisateur
    # et les critiques en réponse à celles de ses abonnements.
    user = request.user
    # Récupérer toutes les critiques de l'utilisateur actuellement connecté
    reviews = Review.objects.filter(user=user, visibility=True)

    # Récupérer les utilisateurs suivis par l'utilisateur actuellement connecté
    followed_users = UserFollows.objects.filter(user=user).values_list(
        "followed_user", flat=True
    )

    # Récupérer toutes les critiques des utilisateurs suivis
    reviews_by_followed_users = Review.objects.filter(
        user__in=followed_users, visibility=True
    )

    # Combiner les critiques de l'utilisateur et celles des utilisateurs suivis
    all_reviews = reviews | reviews_by_followed_users

    return all_reviews


"""Cette fonction récupère toutes les critiques 
visibles pour l'utilisateur en cours, y compris celles
des utilisateurs suivis par l'utilisateur."""


@login_required
def get_users_viewable_tickets(request):
    # Cette méthode récupère tous les tickets visibles pour l'utilisateur
    # et les tickets en réponse à ceux de ses abonnements.
    user = request.user
    # Récupérer tous les tickets de l'utilisateur actuellement connecté
    tickets = Ticket.objects.filter(user=user, visibility=True)

    # Récupérer les utilisateurs suivis par l'utilisateur actuellement connecté
    followed_users = UserFollows.objects.filter(user=user).values_list(
        "followed_user", flat=True
    )

    # Récupérer tous les tickets des utilisateurs suivis
    tickets_by_followed_users = Ticket.objects.filter(
        user__in=followed_users, visibility=True
    )

    # Combiner les tickets de l'utilisateur et ceux des utilisateurs suivis
    all_tickets = tickets | tickets_by_followed_users

    return all_tickets


"""Cette fonction récupère tous les tickets visibles
pour l'utilisateur en cours, y compris ceux des 
utilisateurs suivis par l'utilisateur."""


# TICKET
# creation de la vue de creation d'un ticket simple
@login_required
def create_ticket(request):
    if request.method == "POST":
        ticket_form = TicketForm(request.POST, request.FILES)
        if ticket_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            if "image" in request.FILES:
                ticket.image = request.FILES["image"]
            ticket.save()
            messages.success(request, "Votre ticket a été créé avec succès.")
            return redirect("flux")
    else:
        ticket_form = TicketForm()

    context = {"ticket_form": ticket_form}
    return render(request, "creation-ticket.html", context)
    """ Redirigez vers la page de app/flux après avoir créé le ticket sinon rester sur la page 
        app/nouvelle-critique/ 
    """
    # Si la méthode de la requête n'est pas POST ou si le formulaire n'est pas valide, continuez ici.
    # ticket_form = TicketForm()
    # return render(request, "creation-ticket.html", {"ticket_form": ticket_form})


"""Cette vue permet à l'utilisateur de créer un nouveau ticket. Si la méthode
HTTP est POST et le formulaire est valide, le ticket est créé. Sinon, le 
formulaire vide est affiché."""


@login_required
def modify_ticket(request, ticket_id):
    # Récupérez le ticket à modifier
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    if request.method == "POST":
        form = TicketForm(
            request.POST, instance=ticket
        )  # Pré-remplissez le formulaire avec les données du ticket

        if form.is_valid():
            form.save()  # Enregistrez les modifications si le formulaire est valide
            return redirect(
                "mes-posts"
            )  # Redirigez l'utilisateur vers la liste de ses tickets après la modification
    else:
        form = TicketForm(
            instance=ticket
        )  # Créez une instance du formulaire pré-rempli

    return render(request, "modifier-ticket.html", {"ticket": ticket, "form": form})


""" Cette vue permet à l'utilisateur de modifier un de ses tickets existants.
Si la méthode HTTP est POST et le formulaire est valide, le ticket est modifié.
Sinon, le formulaire est prérempli avec les données actuelles."""


# creation de la vue de suppression d'un ticket
@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    print("**", ticket.id)  # Utilisez ticket.id pour obtenir l'ID du ticket
    print("**", request.method)
    if request.method == "POST":
        # Gérez ici la logique de suppression du ticket
        ticket.delete()
        # mise a jour de la liste des tickets restants
        remaining_tickets = Ticket.objects.filter(user=request.user)
        # Redirigez l'utilisateur vers la liste de ses tickets après la suppression
        return render(request, "mes-posts.html", {"tickets": remaining_tickets})

    return render(request, "mes-posts.html", {"ticket": ticket})


"""Cette vue permet à l'utilisateur de supprimer un de ses tickets
existants. Si la méthode HTTP est POST, le ticket est supprimé. 
Sinon, la page "mes-posts" est affichée."""


# POSTS
# creation de la vue de mes posts
@login_required
def my_posts(request):
    # Récupérer les tickets de l'utilisateur actuellement connecté
    tickets = Ticket.objects.filter(user=request.user)
    print("fonction my_posts", tickets)
    for ticket in tickets:
        print(ticket.id)
        print(ticket.title)
        print(ticket.description)
        print(ticket.image)
        print(ticket.visibility)
        print(ticket.time_created)

    return render(request, "mes-posts.html", {"tickets": tickets})


"""Cette vue affiche les tickets de l'utilisateur actuellement
connecté."""

# CRITIQUE


@login_required
def nouvelle_critique_2(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                critique = form.save(commit=False)
                critique.ticket = ticket
                critique.user = request.user
                critique.save()
                return redirect("flux")
            except IntegrityError:
                messages.error(request, "Vous avez déjà critiqué ce ticket.")
                return redirect("flux")
    else:
        form = ReviewForm()
    return render(request, "nouvelle-critique-2.html", {"ticket": ticket, "form": form})


# creation de la vue de creation d'une critique simple
@login_required
def create_review(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == "POST":
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            messages.success(request, "Votre critique a été créée avec succès.")
            return redirect("view_ticket", ticket_id=ticket.id)
    else:
        review_form = ReviewForm()

    context = {"ticket": ticket, "review_form": review_form}
    return render(request, "create_review.html", context)


"""Cette vue permet à l'utilisateur de créer une nouvelle critique.
Si la méthode HTTP est POST et le formulaire est valide, la 
critique est créée. Sinon, le formulaire vide est affiché."""

# creation de la vue combine critique et ticket


@login_required
def create_combined(request):
    if request.method == "POST":
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)
        if ticket_form.is_valid() and review_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            # Traite les données des deux formulaires
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()

            # ticket_data = ticket_form.cleaned_data
            # review_data = review_form.cleaned_data

            return redirect("flux")  # Redirigez l'utilisateur vers le flux

    else:
        ticket_form = TicketForm()
        review_form = ReviewForm()

    return render(
        request,
        "nouvelle-critique.html",
        {"ticket_form": ticket_form, "review_form": review_form},
    )


"""Cette vue permet à l'utilisateur de créer à la fois un ticket
et une critique. Si les deux formulaires sont valides, le contenu
est créé."""


@login_required
def review_response(request):
    return render(request, "reponse-critique.html")


@login_required
def modify_review(request):
    return render(request, "modifier-critique.html")


@login_required
def view_review(request, review_id):
    # Récupérez la critique en fonction de son ID, ou renvoyez une erreur 404 si elle n'existe pas
    review = get_object_or_404(Review, id=review_id)

    # Vous pouvez maintenant utiliser l'objet 'review' pour accéder aux données de la critique
    # Par exemple, review.title, review.rating, review.comment, etc.

    return render(request, "nom_de_votre_template.html", {"review": review})


"""Cette vue permet à l'utilisateur de voir une critique spécifique."""


@login_required
def view_ticket(request, ticket_id):
    # Récupérez la critique en fonction de son ID, ou renvoyez une erreur 404 si elle n'existe pas
    ticket = get_object_or_404(Review, id=ticket_id)

    # Vous pouvez maintenant utiliser l'objet 'review' pour accéder aux données de la critique
    # Par exemple, review.title, review.rating, review.comment, etc.

    return render(request, "nom_de_votre_template.html", {"review": ticket})


"""Cette vue permet à l'utilisateur de voir un ticket spécifique en 
fonction de son ID. Elle récupère le ticket correspondant à l'ID 
fourni et l'affiche. Si le ticket n'existe pas, elle renvoie une erreur 404."""

# ABONNEMENT

"""Cette vue gère la recherche d'utilisateurs.
Elle renvoie une réponse JSON contenant des 
utilisateurs correspondant à la requête de recherche."""


@login_required
def available_users(request):
    form = SubscriptionForm(request.POST or None)
    message = ""

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            try:
                user_to_subscribe = User.objects.get(username=username)
            except User.DoesNotExist:
                message = "Utilisateur non trouvé"
            else:
                # Récupérez tous les abonnements de l'utilisateur actuel
                subscriptions = UserFollows.objects.filter(user=request.user)
                followed_users = [
                    subscription.followed_user.username
                    for subscription in subscriptions
                ]

                if user_to_subscribe.username in followed_users:
                    message = "Déjà abonné"
                else:
                    # Créez un nouvel abonnement
                    subscription = UserFollows(
                        user=request.user, followed_user=user_to_subscribe
                    )
                    subscription.save()
                    message = "Abonnement réussi"
    # creation de la liste des utilisateurs auquel l'utilisateur est abonné
    subscriptions = UserFollows.objects.filter(user=request.user)
    followed_users = [subscription.followed_user
                      for subscription in subscriptions]
    # creation de la liste des followers de l'utilisateur
    # followers = UserFollows.objects.filter(followed_user=request.user)
    followers_users = [
        subscription.user
        for subscription in UserFollows.objects.filter(
            followed_user=request.user)
    ]
    context = {
        "form": form,
        "message": message,
        "followed_users": followed_users,
        "followers_users": followers_users,
    }

    return render(request, "available_users.html", context)


"""Cette vue affiche les utilisateurs disponibles pour l'abonnement.
Elle gère également la recherche d'utilisateurs. Si la méthode HTTP 
est GET, elle récupère les utilisateurs en fonction de la recherche."""


@login_required
def followers(request):
    # Récupérez les utilisateurs qui suivent l'utilisateur connecté
    followers = Subscription.objects.filter(following=request.user)

    return render(request, "followers.html", {"followers": followers})


""" Cette vue affiche les utilisateurs qui suivent l'utilisateur
actuellement connecté."""


@login_required
def get_subscriptions(request):
    subscriptions = UserFollows.objects.filter(user=request.user)
    followed_users = [
        subscription.followed_user.username for subscription in subscriptions
    ]
    return render(request, "subscriptions.html", {"followed_users": followed_users})


"""Ces vues permettent à l'utilisateur de suivre ou de cesser 
de suivre un autre utilisateur."""


@login_required
def unfollow(request, user_id):
    user_to_unfollow = User.objects.get(id=user_id)
    UserFollows.objects.filter(
        user=request.user, followed_user=user_to_unfollow
    ).delete()
    return redirect("available_users")


"""Cette vue permet à l'utilisateur de cesser de suivre un autre 
utilisateur. Elle supprime l'instance de l'abonnement qui lie 
l'utilisateur actuel à l'utilisateur cible, puis redirige 
l'utilisateur vers la page "available_users". Cela permet de 
mettre à jour la liste des utilisateurs auxquels l'utilisateur 
actuel est abonné."""


@login_required
def subscription(request):  # fonction pour s'abonner a un utilisateur
    print("subscription appelée")
    user_search_form = UserSearchForm()
    # Obtenez la liste des utilisateurs que l'utilisateur connecté suit déjà
    following_users = Subscription.objects.filter(
        follower=request.user).values_list(
        "following", flat=True
    )
    # Obtenez la liste des utilisateurs qui suivent l'utilisateur connecté
    followers = Subscription.objects.filter(following=request.user)

    if request.method == "POST":
        # Traitez le formulaire de recherche d'utilisateur
        user_search_form = UserSearchForm(request.POST)
        if user_search_form.is_valid():
            # Récupérez l'utilisateur recherché à partir du formulaire
            searched_users = user_search_form.search_users()

            if searched_users is not None and len(searched_users) > 0:
                searched_user = searched_users[0]
                # Créez une instance de Subscription pour l'abonnement
                subscription = Subscription(
                    follower=request.user, following=searched_user
                )
                print(str(subscription) + " subscription")
                subscription.save()
            else:
                print("Aucun utilisateur trouvé")

    return render(
        request,
        "available_users.html",
        {
            "user_search_form": user_search_form,
            "following_users": following_users,
            "followers": followers,
        },
    )


"""Cette vue gère la page d'abonnement. 
Elle permet à l'utilisateur de rechercher
, suivre et afficher ses abonnements et ses abonnés."""


@login_required
def subscribe_user(request):
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            try:
                user_to_subscribe = User.objects.get(username=username)
                Subscription.objects.create(
                    user=request.user, subscribed_to=user_to_subscribe
                )
                messages.success(request, "Abonnement réussi.")
            except User.DoesNotExist:
                messages.error(request, "Utilisateur non trouvé.")
    else:
        form = SubscriptionForm()

    return render(request, "available_users.html", {"form": form})


@login_required
def follow(request, user_id):
    user_to_follow = User.objects.get(id=user_id)
    UserFollows.objects.create(user=request.user, followed_user=user_to_follow)
    return redirect("some-view-name")
