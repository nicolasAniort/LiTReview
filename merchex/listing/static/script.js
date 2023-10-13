document.addEventListener("DOMContentLoaded", function() {
    const deleteLinks = document.querySelectorAll(".delete-link");
    deleteLinks.forEach(link => {
        link.addEventListener("click", function(event) {
            event.preventDefault();
            const ticketId = this.getAttribute("data-ticket-id");
            console.log("Ticket ID:", ticketId);
            const confirmDelete = confirm("Voulez-vous vraiment supprimer ce ticket ?");
            console.log("Confirmation:", confirmDelete);
            if (confirmDelete) {
                window.location.href = "/app/mes-posts";
            }
        });
    });

    const userSearchInput = document.querySelector("#search-input");
    const userItems = document.querySelectorAll("[data-username]");
    const subscribeButton = document.querySelector("#subscribe-button");  // Bouton d'abonnement

    let selectedUserId = null;  // Variable pour stocker l'ID de l'utilisateur sélectionné

    userSearchInput.addEventListener("input", function() {
        const searchTerm = userSearchInput.value;
        selectedUserId = null;  // Réinitialisez l'ID de l'utilisateur sélectionné

        // Effectuez une requête AJAX pour rechercher les utilisateurs sur le serveur
        // Assurez-vous que l'URL correspond à votre vue Django qui gère la recherche d'utilisateurs.
        fetch(`/app/available_users/?search=${searchTerm}`)
            .then(response => response.json())
            .then(data => {
                // Supprimez d'abord les anciens résultats
                userItems.forEach(userItem => {
                    userItem.style.display = "none";
                });

                // Parcourez les données renvoyées par le serveur
                data.users.forEach(user => {
                    const userId = user.id;

                    userItems.forEach(userItem => {
                        if (userItem.getAttribute("data-username") === userId.toString()) {
                            userItem.style.display = "block";

                            // Ajoutez un gestionnaire d'événements pour sélectionner cet utilisateur
                            userItem.addEventListener('click', function() {
                                const userId = user.getAttribute('data-username');
                                selectedUserId = userId;  // Stockez l'ID de l'utilisateur sélectionné
                            });
                        }
                    });
                });
            })
            .catch(error => {
                console.error("Erreur lors de la recherche d'utilisateurs :", error);
            });
    });

    // Ajoutez un gestionnaire d'événements pour le bouton d'abonnement
    subscribeButton.addEventListener('click', function() {
        console.log("S'abonner button is clicked.");
        if (selectedUserId) {
            console.log("selectUserId", selectedUserId);
            fetch(`/app/subscribe/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/x-www-form-urlencoded',  // Assurez-vous que le type de contenu est correct
                },
                body: `user_id=${selectedUserId}`,  // Vous devez ajuster ce nom de champ en fonction de votre modèle de données
            })
            .then(response => response.json())
            .then(result => {
                console.log("Subscription result:", result);
                // Réagissez en fonction du résultat de l'abonnement
                console.log(result);
            })
            .catch(error => {
                console.error("Erreur lors de l'abonnement :", error);
            });
        }
    });
});

// Fonction pour obtenir le jeton CSRF depuis les cookies
function getCSRFToken() {
    const csrfCookie = document.cookie
        .split(";")
        .find(cookie => cookie.trim().startsWith("csrftoken="));
    if (csrfCookie) {
        return csrfCookie.split("=")[1];
    }
    return "";
}
//suite
document.addEventListener("DOMContentLoaded", function() {
    // Votre code JavaScript existant ...

    // Lorsque la page est chargée, récupérez les abonnements et ajoutez-les à la liste des abonnements
    fetch("/app/get_subscriptions/")  // Remplacez l'URL par celle de votre vue Django qui renvoie la liste des abonnements
        .then(response => response.json())
        .then(data => {
            const subscriptionsList = document.getElementById("subscriptions-list");

            // Parcourez les abonnements renvoyés par le serveur
            data.subscriptions.forEach(subscription => {
                const userId = subscription.id;
                const username = subscription.username;

                // Créez un élément de liste pour cet abonnement
                const listItem = document.createElement("li");
                listItem.textContent = username;

                // Ajoutez un bouton "Désabonner" à côté du nom de l'utilisateur
                const unsubscribeButton = document.createElement("button");
                unsubscribeButton.textContent = "Désabonner";
                unsubscribeButton.addEventListener("click", function() {
                    // Logique pour gérer la désabonnement de cet utilisateur
                    fetch(`/app/unfollow/${userId}`, {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": getCSRFToken(), // Assurez-vous d'obtenir le jeton CSRF correctement
                        },
                    })
                    .then(response => response.json())
                    .then(result => {
                        // Réagissez en fonction du résultat du désabonnement
                        console.log(result);

                        // Supprimez cet élément de la liste des abonnements
                        subscriptionsList.removeChild(listItem);
                    })
                    .catch(error => {
                        console.error("Erreur lors du désabonnement :", error);
                    });
                });

                listItem.appendChild(unsubscribeButton);
                subscriptionsList.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error("Erreur lors de la récupération des abonnements :", error);
        });

    // Votre code JavaScript existant ...
});

// Fonction pour obtenir le jeton CSRF depuis les cookies (identique à celle que vous avez déjà)
function getCSRFToken() {
    const csrfCookie = document.cookie
        .split(";")
        .find(cookie => cookie.trim().startsWith("csrftoken="));
    if (csrfCookie) {
        return csrfCookie.split("=")[1];
    }
    return "";
}