import django.urls
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from listing.forms import SignUpForm, ReviewForm, TicketForm
from .models import Ticket, Review, UserFollows, Subscription, User
from listing import views
from itertools import chain
from django.db.models import CharField, Value
from .forms import UserSearchForm
from django.http import JsonResponse, HttpResponse

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
        chain(reviews, tickets), key=lambda post: post.time_created, reverse=True
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
            ticket.user = (
                request.user
            )  # Associez le ticket à l'utilisateur actuellement connecté
            ticket.save()
            if django.urls.re_path(
                r"^app/creation-ticket/", views.create_ticket, name="creation-ticket"
            ):
                return redirect("flux")
        """ Redirigez vers la page de app/flux après avoir créé le ticket sinon rester sur la page 
            app/nouvelle-critique/ 
        """
    # Si la méthode de la requête n'est pas POST ou si le formulaire n'est pas valide, continuez ici.
    ticket_form = TicketForm()

    return render(request, "creation-ticket.html", {"ticket_form": ticket_form})


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

@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    print("**", ticket.id)  # Utilisez ticket.id pour obtenir l'ID du ticket

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
    print(tickets)
    return render(request, "mes-posts.html", {"tickets": tickets})


"""Cette vue affiche les tickets de l'utilisateur actuellement
connecté."""

# CRITIQUE
# creation de la vue de creation d'une critique simple
@login_required
def create_review(request):
    # Initialisation du formulaire de ticket
    ticket_form = TicketForm()

    if request.method == "POST":
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            # Créez une instance de Review et enregistrez-la dans la base de données
            review = Review(
                title=review_form.cleaned_data["title"],
                rating=review_form.cleaned_data["rating"],
                comment=review_form.cleaned_data["comment"],
                # Vous devrez ajouter d'autres champs en fonction de votre modèle
            )
            review.save()
            return redirect("flux")  # Redirigez l'utilisateur vers le flux
    else:
        review_form = ReviewForm()

    return render(
        request,
        "nouvelle-critique.html",
        {"review_form": review_form, "ticket_form": ticket_form},
    )


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
            # Traitez les données des deux formulaires comme vous le souhaitez
            ticket_data = ticket_form.cleaned_data
            review_data = review_form.cleaned_data

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

# Abonnement


@login_required
def search_users(request):
    search_query = request.GET.get('search_query', '')
    users = User.objects.filter(username__icontains=search_query).exclude(id=request.user.id)
    user_data = [{'id': user.id, 'username': user.username} for user in users]
    print(user_data)
    return JsonResponse({'users': user_data})
    

"""Cette vue gère la recherche d'utilisateurs.
Elle renvoie une réponse JSON contenant des 
utilisateurs correspondant à la requête de recherche."""

@login_required
def available_users(request):
    if request.method == 'GET':
        search_term = request.GET.get('search', '')
        users = User.objects.exclude(id=request.user.id)

        # Si un terme de recherche est fourni, filtrez les utilisateurs
        if search_term:
            users = users.filter(username__icontains=search_term)

        subscriptions = Subscription.objects.filter(follower=request.user)
        subscription_data = []
        
        for subscription in subscriptions:
            user_data = {
                "id": subscription.following.id,
                "username": subscription.following.username
            }
            subscription_data.append(user_data)

        return render(request, 'available_users.html', {"subscriptions": subscription_data})
    
    elif request.method == 'POST':
        # Logique pour gérer l'abonnement à un utilisateur
        user_id = request.POST.get('user_id')  # Vous devrez ajuster ceci en fonction de votre modèle de données
        try:
            # Vérifiez si l'abonnement existe déjà
            subscription = Subscription.objects.get(follower=request.user, following_id=user_id)
            # Si l'abonnement existe, supprimez-le pour permettre de se désabonner
            subscription.delete()
            message = 'Désabonnement réussi'
        except Subscription.DoesNotExist:
            # Si l'abonnement n'existe pas, créez-le pour s'abonner
            subscription = Subscription(follower=request.user, following_id=user_id)
            subscription.save()
            message = 'Abonnement réussi'

        return JsonResponse({'message': message})

    else:
        # Gérez d'autres méthodes HTTP si nécessaire
        return HttpResponse(status=405)


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
def follow(request, user_id):
    # Créez une instance de Subscription pour suivre un utilisateur
    if request.method == "POST":
        # Logique pour s'abonner à l'utilisateur avec user_id
        # Assurez-vous de gérer l'abonnement correctement et de renvoyer 
        # une réponse JSON appropriée
        return JsonResponse({"message": "Abonnement réussi"})

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
    """following_user = User.objects.get(id=user_id)
    subscription = Subscription(follower=request.user,
    following=following_user)
    subscription.save()
    
    return redirect('available_users')"""


"""Ces vues permettent à l'utilisateur de suivre ou de cesser 
de suivre un autre utilisateur."""

@login_required
def unfollow(request, user_id):
    # Supprimez une instance de Subscription pour cesser de suivre un utilisateur
        following_user = User.objects.get(id=user_id)
        Subscription.objects.filter(
            follower=request.user, following=following_user
        ).delete()

    # Redirigez l'utilisateur vers la page app/available_user
        return redirect("available_users")


"""Cette vue permet à l'utilisateur de cesser de suivre un autre 
utilisateur. Elle supprime l'instance de l'abonnement qui lie 
l'utilisateur actuel à l'utilisateur cible, puis redirige 
l'utilisateur vers la page "available_users". Cela permet de 
mettre à jour la liste des utilisateurs auxquels l'utilisateur 
actuel est abonné."""

@login_required
def subscription(request):
    print("subscription appeléé")
    user_search_form = UserSearchForm()
    # Obtenez la liste des utilisateurs que l'utilisateur connecté suit déjà
    following_users = Subscription.objects.filter(user=request.user).values_list(
        "searched_user", flat=True
    )
    # Obtenez la liste des utilisateurs qui suivent l'utilisateur connecté
    followers = Subscription.objects.filter(searched_user=request.user)

    if request.method == "POST":
        # Traitez le formulaire de recherche d'utilisateur
        user_search_form = UserSearchForm(request.POST)
        if user_search_form.is_valid():
            # Récupérez l'utilisateur recherché à partir du formulaire
            searched_user = user_search_form.cleaned_data["searched_query"]

            # Créez une instance de Subscription pour l'abonnement
            subscription = Subscription(user=request.user, searched_user=searched_user)
            print(subscription + "subscription")
            subscription.save()

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
    print("subscribe_user appelé")
    print("request", request)
    if request.method == "POST":
        print("entree dans le if du post")
        user_id = request.POST.get("user_id")
        print("POST OK")
        if user_id:
            try:
                # Récupérez l'utilisateur à qui vous souhaitez vous abonner
                user_to_subscribe = User.objects.get(id=user_id)

                # Vérifiez si vous n'êtes pas déjà abonné à cet utilisateur
                existing_subscription = Subscription.objects.filter(
                    follower=request.user,
                    following=user_to_subscribe
                ).exists()

                if not existing_subscription:
                    # Créez une instance de Subscription pour enregistrer l'abonnement
                    new_subscription = Subscription(
                        follower=request.user,
                        following=user_to_subscribe
                    )
                    new_subscription.save()

                    return JsonResponse({"message": "Abonnement réussi"})
                else:
                    return JsonResponse({"error": "Vous êtes déjà abonné à cet utilisateur."})
            except User.DoesNotExist:
                return JsonResponse({"error": "Cet utilisateur n'existe pas."})
            except Exception as e:
                return JsonResponse({"error": str(e)})

    return JsonResponse({"error": "L'abonnement a échoué"})

@login_required
def get_subscriptions(request):
    print(request)
    if request.user.is_authenticated:
        # Récupérez les abonnements de l'utilisateur connecté
        subscriptions = Subscription.objects.filter(follower=request.user)
        subscription_data = [{"id": subscription.following.id, "username": subscription.following.username} for subscription in subscriptions]

        return JsonResponse({"subscriptions": subscription_data})

    return JsonResponse({"error": "Vous devez être connecté pour obtenir des abonnements."})