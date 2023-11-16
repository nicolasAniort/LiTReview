# LITRevu
 application web pour notre MVP (minimum viable product, ou produit viable minimum),  produit permettant à une communauté d'utilisateurs de publier des critiques de livres ou d’articles et de consulter ou de solliciter une critique de livres à la demande.
## Configuration locale

1. **Clonez le dépôt** : Clonez le dépôt sur votre machine locale en utilisant la commande `git clone url_du_dépôt`.

2. **Créez un environnement virtuel** : Créez un nouvel environnement virtuel Python en utilisant la commande `python3 -m venv env`.

3. **Activez l'environnement virtuel** : Activez l'environnement virtuel en utilisant la commande `source env/bin/activate` sur Unix ou `.\env\Scripts\activate` sur Windows.

4. **Installez les dépendances** : Installez les dépendances du projet en utilisant la commande `pip install -r requirements.txt`.

5. **Configurez la base de données** : Configurez la base de données en utilisant les commandes `python manage.py makemigrations` et `python manage.py migrate`.

6. **Lancez le serveur** : Lancez le serveur de développement local en utilisant la commande `python manage.py runserver`.

Vous devriez maintenant pouvoir accéder à l'application en ouvrant votre navigateur et en allant à `http://127.0.0.1:8000`.
