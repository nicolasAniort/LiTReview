document.addEventListener("DOMContentLoaded", function() {
    const deleteLinks = document.querySelectorAll(".delete-link");
    const userSearchInput = document.querySelector("#search-input");
    const userItems = document.querySelectorAll("[data-username]");
    const subscribeButton = document.querySelector("#subscribe-button");
    let dataList = document.querySelector("#user-list"); // L'élément datalist
    let selectedUserId = null;
    let users = [];

    function getCSRFToken() {
        const csrfCookie = document.cookie
            .split(";")
            .find(cookie => cookie.trim().startsWith("csrftoken="));
        if (csrfCookie) {
            return csrfCookie.split("=")[1];
        }
        return "";
    }

    // Fonction pour ajouter des options au datalist
    function populateDataList() {
        dataList.innerHTML = "";
        users.forEach(user => {
            let option = document.createElement("option");
            option.value = user.username;
            option.id = user.id;
            dataList.appendChild(option);
        });
    }

    // Écouteur d'événement pour le champ de recherche
    userSearchInput.addEventListener("input", function() {
        const searchTerm = userSearchInput.value;
        selectedUserId = null;
        fetch(`/app/search_users/?search_query=${searchTerm}`)
            .then(response => response.json())
            .then(data => {
                userItems.forEach(userItem => {
                    userItem.style.display = "none";
                });

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

    // Écouteur d'événement pour le bouton d'abonnement
    subscribeButton.addEventListener('click', function() {
        console.log("selectedUserId:", selectedUserId);
        if (selectedUserId) {
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
// fonction gerant labonnement à un utilisateur

document.addEventListener("DOMContentLoaded", function() { 
    //L'événement "DOMContentLoaded" est utilisé pour s'assurer que le script
    // est exécuté une fois que le document HTML a été entièrement chargé
      const searchInput = document.querySelector("#search-input");
      console.log(searchInput);
    // Représente l'élément HTML avec l'ID "search-input"
      const userDatalist = document.querySelector("#user-list");
      console.log(userDatalist);
      // Représente l'élément HTML avec l'ID "search-results"
      const searchForm = document.querySelector("#search-form");
      console.log(searchForm);
      // Représente l'élément HTML avec l'ID "search-form"
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