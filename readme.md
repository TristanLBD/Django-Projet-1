# 🚀 France Chômage - Plateforme de Candidature

Une plateforme moderne de gestion des candidatures d'emploi développée avec Django, permettant aux entreprises de publier des offres et aux candidats de postuler facilement.

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Technologies utilisées](#-technologies-utilisées)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [API](#-api)
- [Structure du projet](#-structure-du-projet)
- [Comptes de test](#-comptes-de-test)

## ✨ Fonctionnalités

### 👥 Gestion des utilisateurs
- **Candidats** : Création de profil, candidatures, suivi des postulations
- **Employeurs** : Gestion d'entreprises, publication d'offres, suivi des candidatures
- **Administrateurs** : Supervision complète, statistiques, gestion des utilisateurs

### 💼 Gestion des offres d'emploi
- Publication d'offres avec descriptions détaillées
- Filtrage par localisation, type de contrat, niveau d'expérience
- Support du télétravail
- Système de candidatures avec lettres de motivation

### 🏢 Gestion des entreprises
- Profils d'entreprises complets
- Logos et photos d'entreprise
- Informations de contact détaillées

### 📊 Tableaux de bord
- **Dashboard candidat** : Suivi des candidatures, offres recommandées
- **Dashboard employeur** : Statistiques par entreprise, gestion des candidatures
- **Dashboard admin** : Vue d'ensemble complète, statistiques globales

### 🔄 API et exports
- Export CSV des candidatures (quotidien et complet)
- Import CSV des candidatures
- API REST pour l'intégration externe

## 🛠 Technologies utilisées

- **Backend** : Django 5.1, Python 3.11+
- **Base de données** : SQLite (développement) / PostgreSQL (production)
- **Frontend** : Bootstrap 5, HTML5, CSS3, JavaScript
- **Authentification** : Django Auth System
- **API** : Django REST Framework
- **Emails** : Django Email Backend
- **Interface admin** : Django Admin personnalisé

## 🚀 Installation

### Prérequis

- Python 3.11 ou supérieur
- pip (gestionnaire de paquets Python)
- Git

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone https://github.com/TristanLBD/Django-Projet-1.git
cd "Projet Django 2"
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer la base de données**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Initialiser les données de test**
```bash
python init_db.py
```

6. **Lancer le serveur**
```bash
python manage.py runserver
```

## ⚙️ Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
SECRET_KEY=votre-clé-secrète-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3

# Configuration email (optionnel)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
```

### Configuration de la base de données

Pour la production, modifiez `job_platform/settings.py` :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nom_de_votre_db',
        'USER': 'utilisateur_db',
        'PASSWORD': 'mot_de_passe_db',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📖 Utilisation

### Accès aux interfaces

- **Site principal** : http://127.0.0.1:8000/
- **Administration** : http://127.0.0.1:8000/admin/
- **API** : http://127.0.0.1:8000/api/

### Workflow typique

1. **Création d'un compte employeur**
   - Inscription via l'interface web
   - Création d'un profil d'entreprise

2. **Publication d'une offre**
   - Remplir le formulaire d'offre d'emploi
   - Définir les critères (localisation, salaire, etc.)
   - Publier l'offre

3. **Candidature d'un utilisateur**
   - Parcourir les offres disponibles
   - Postuler avec une lettre de motivation
   - Suivre le statut de la candidature

4. **Gestion par l'employeur**
   - Recevoir les notifications de candidatures
   - Examiner les profils des candidats
   - Mettre à jour le statut des candidatures

## 🔌 API

### Endpoints disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/export/applications/today/` | GET | Export CSV des candidatures du jour |
| `/api/export/applications/all/` | GET | Export CSV de toutes les candidatures |
| `/api/import/applications/` | POST | Import CSV de candidatures |

### Format CSV pour l'import

```csv
candidate_email;candidate_first_name;candidate_last_name;job_title;company_name;cover_letter;status
john.doe@email.com;John;Doe;Développeur Python;TechCorp Solutions;Lettre de motivation...;PENDING
```

### Exemple d'utilisation

```bash
# Export des candidatures du jour
curl http://127.0.0.1:8000/api/export/applications/today/

# Import de candidatures
curl -X POST -F "csv_file=@candidatures.csv" http://127.0.0.1:8000/api/import/applications/
```

## 📁 Structure du projet

```
Projet Django 2/
├── accounts/                 # Gestion des utilisateurs
├── api/                     # API REST et exports
├── companies/               # Gestion des entreprises
├── jobs/                    # Gestion des offres et candidatures
├── job_platform/           # Configuration principale
├── templates/              # Templates HTML
├── static/                 # Fichiers statiques
├── media/                  # Fichiers uploadés
├── init_db.py             # Script d'initialisation
├── requirements.txt        # Dépendances Python
└── readme.md              # Documentation
```

## 👥 Comptes de test

Après avoir lancé `python init_db.py`, les comptes suivants sont créés :

### Candidat
- **Utilisateur** : `testuser`
- **Mot de passe** : `testpass123`

### Employeurs
- **TechCorp** : `techcorp_employer` / `techcorp123`
- **Digital Marketing** : `digital_employer` / `digital123`
- **Green Energy** : `green_employer` / `green123`
- **Finance Consulting** : `finance_employer` / `finance123`
- **Creative Design** : `creative_employer` / `creative123`

### Administrateur
- **Utilisateur** : `admin`
- **Mot de passe** : `admin123`
- *À créer manuellement avec `python manage.py createsuperuser`*

## 🚀 Déploiement

### Préparation pour la production

1. **Sécurité**
```bash
# Générer une nouvelle clé secrète
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

2. **Variables d'environnement**
```env
DEBUG=False
SECRET_KEY=votre-nouvelle-cle-secrete
ALLOWED_HOSTS=votre-domaine.com
```

3. **Base de données**
```bash
python manage.py collectstatic
python manage.py migrate
```

### Plateformes recommandées

- **Heroku** : Déploiement simple avec PostgreSQL
- **DigitalOcean** : VPS avec contrôle total
- **AWS** : Services cloud scalables
- **PythonAnywhere** : Hébergement spécialisé Python

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Contacter l'équipe de développement

---

**Développé avec ❤️ pour simplifier le processus de recrutement**
