const userItems = document.querySelectorAll("[data-username]"); // Éléments liés aux utilisateurs
const deleteLinks = document.querySelectorAll(".delete-link"); // Liens pour supprimer des éléments
let dataList = document.querySelector("#user-list"); // Datalist pour les suggestions
let users = []; // Stocke la liste des utilisateurs

document.addEventListener("DOMContentLoaded", function() {
// Sélectionnez les éléments HTML dont vous avez besoin
const userSearchInput = document.querySelector("#searchInput"); // Champ de recherche
console.log("initialisation",userSearchInput);
const userDatalist = document.querySelector("#user-list");
const subscribeButton = document.querySelector("#subscribe-button"); // Bouton d'abonnement
let selectedUserId = null; // Stocke l'ID de l'utilisateur sélectionné
let users = []; // Stocke la liste des utilisateurs

// ABONNEMENT: Fonction pour ajouter des options au datalist
function populateDataList() {
    userDatalist.innerHTML = "";
    users.forEach(user => {
        let option = document.createElement("option");
        option.value = user.username;
        option.id = user.id;
        userDatalist.appendChild(option);
    });
}

// ABONNEMENT: Écouteur d'événement pour le champ de recherche
console.log("Abonnement",userSearchInput);
userSearchInput.addEventListener("input", function() {
    console.log("Écouteur d'événement pour le champ de recherche");
    const searchTerm = userSearchInput.value;
    console.log("searchTerm",searchTerm);
    selectedUserId = null;
    fetch(`/app/search_users/?search_query=${searchTerm}`)
        .then(response => response.json())
        .then(data => {
            // Masquez tous les éléments d'utilisateur
            userItems.forEach(userItem => {
                userItem.style.display = "none";
            });

            // Affichez les utilisateurs correspondant à la recherche
            data.users.forEach(user => {
                const userId = user.id;
                userItems.forEach(userItem => {
                    if (userItem.getAttribute("data-username") === userId.toString()) {
                        userItem.style.display = "block";
                        userItem.addEventListener('click', function() {
                            const userId = user.getAttribute('data-username');
                            selectedUserId = userId;
                        });
                    }
                });
            });

            // Mise à jour de la liste des utilisateurs et du datalist
            users = data.users;
            populateDataList();
        })
        .catch(error => {
            console.error("Erreur lors de la recherche d'utilisateurs :", error);
        });
});

// ABONNEMENT: Écouteur d'événement pour le bouton d'abonnement
subscribeButton.addEventListener('click', function() {
    console.log("Écouteur d'événement pour le bouton d'abonnement selectedUserId:", selectedUserId);
    if (selectedUserId) {
        // Effectuez une requête pour abonner l'utilisateur
        fetch(`/app/subscribe_user/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `user_id=${selectedUserId}`,
        })
        .then(response => response.json())
        .then(result => {
            console.log("Subscription result:", result);
        })
        .catch(error => {
            console.error("Erreur lors de l'abonnement :", error);
        });
    }
});

// Fonction principale pour gérer les interactions sur la page une fois que le document est chargé
document.addEventListener("DOMContentLoaded", function() {
    // Sélectionnez les éléments HTML dont vous avez besoin
    

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

    // Lorsque la page est chargée, récupérez les abonnements et ajoutez-les à la liste des abonnements
    fetch("/app/get_subscriptions/")
        .then(response => response.json())
        .then(data => {
            const subscriptionsList = document.getElementById("subscriptions-list");
            data.subscriptions.forEach(subscription => {
                const userId = subscription.id;
                const username = subscription.username;
                const listItem = document.createElement("li");
                listItem.textContent = username;
                const unsubscribeButton = document.createElement("button");
                unsubscribeButton.textContent = "Désabonner";

                // Écouteur d'événement pour le bouton de désabonnement
                unsubscribeButton.addEventListener("click", function() {
                    fetch(`/app/unfollow/${userId}`, {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": getCSRFToken(),
                        },
                    })
                    .then(response => response.json())
                    .then(result => {
                        console.log(result);
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
});

// Nouvelle fonction pour gérer les interactions avec le champ de recherche
document.addEventListener("DOMContentLoaded", function() { 
    const searchInput = document.querySelector("#searchInput");
    const userDatalist = document.querySelector("#user-list");
    const searchForm = document.querySelector("#search-form");
    searchInput.addEventListener("input", function() {
        const searchQuery = searchInput.value;
        fetch(`/app/search_users/?search_query=${searchQuery}`)
            .then(response => response.json())
            .then(data => {
                const userResults = data.users.map(user => user.username).join('\n');
                userDatalist.innerHTML = userResults;
            });
    });
});

// Écouteur d'événement pour le bouton d'abonnement

searchInput = document.querySelector("#searchInput");
console.log(searchInput);
selectedUserId = searchInput.id; // Stocke l'ID de l'utilisateur sélectionné
subscribeButton.addEventListener('click', function() {
    if (selectedUserId) {
        // Effectuez une requête pour enregistrer l'abonnement de l'utilisateur
        fetch(`/app/subscribe_user/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `user_id=${selectedUserId}`,
        })
        .then(response => response.json())
        .then(result => {
            // Gérez la réponse du serveur, par exemple, affichez un message de confirmation
            console.log("Subscription result:", result);
            alert('Abonnement réussi !');
        })
        .catch(error => {
            console.error("Erreur lors de l'abonnement :", error);
            alert('Erreur lors de l\'abonnement.');
        });
    } else {
        alert('Veuillez sélectionner un utilisateur avant de vous abonner.');
    }
});
});