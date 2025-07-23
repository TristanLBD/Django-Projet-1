# Plateforme de Dépôt de Candidature

Plateforme Django pour la gestion des candidatures d'emploi.

## Installation

### Prérequis

-   Python 3.11+
-   pip

### Installation

```bash
# Installer les dépendances
pip install django djangorestframework pillow python-decouple

# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un super utilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

## Accès

-   Admin : http://127.0.0.1:8000/admin/
-   API : http://127.0.0.1:8000/api/export/applications/today/

## Fonctionnalités

-   Gestion des entreprises et offres d'emploi
-   Système de candidatures
-   Export CSV des données
-   Interface d'administration personnalisée
