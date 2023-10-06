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
                // Redirigez directement vers la page mes-posts après la suppression
                window.location.href = "/app/mes-posts";
            }
        });
    });
});