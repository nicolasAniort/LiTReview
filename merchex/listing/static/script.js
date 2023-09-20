document.addEventListener("DOMContentLoaded", function() {
    const deleteLinks = document.querySelectorAll(".delete-link");

    deleteLinks.forEach(link => {
        link.addEventListener("click", function(event) {
            event.preventDefault();
            const ticketId = this.getAttribute("data-ticket-id");
            const confirmDelete = confirm("Voulez-vous vraiment supprimer ce ticket ?");

            if (confirmDelete) {
                // Redirigez vers la vue de suppression
                window.location.href = "{% url 'delete_ticket' %}" + ticketId + "/";
            }
        });
    });
});