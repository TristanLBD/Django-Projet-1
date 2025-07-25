# 🏢 France Chômage - Plateforme de Candidature

Une plateforme moderne de recherche d'emploi et de candidature développée avec Django, permettant aux candidats de postuler et aux employeurs de gérer leurs offres d'emploi.

## ✨ Fonctionnalités

### 👤 **Pour les Candidats**
- 📝 Création de profil utilisateur
- 🔍 Recherche et consultation d'offres d'emploi
- 📄 Candidature en ligne avec lettre de motivation
- 📊 Suivi des candidatures (en attente, acceptée, refusée)
- 📧 Notifications par email

### 👔 **Pour les Employeurs**
- 🏢 Gestion d'entreprise et profil
- 💼 Publication d'offres d'emploi
- 📋 Gestion des candidatures reçues
- 📊 Tableau de bord employeur
- 📧 Notifications automatiques

### 🔧 **Administration**
- ⚙️ Interface d'administration Django complète
- 📊 Statistiques et rapports
- 📥 Import/Export CSV des candidatures
- 🔐 Gestion des utilisateurs et permissions

## 🛠️ Technologies

- **Backend** : Django 4.2+
- **Base de données** : PostgreSQL (Docker) / SQLite (local)
- **Frontend** : Bootstrap 5, HTML5, CSS3
- **API** : Django REST Framework
- **Containerisation** : Docker & Docker Compose
- **Email** : SMTP intégré

## 🚀 Installation

### **Option 1 : Installation Locale**

#### Prérequis
- Python 3.11+
- pip

#### Étapes
```bash
# 1. Cloner le projet
git clone https://github.com/TristanLBD/Django-Projet-1.git
cd "Projet Django 2"

# 2. Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer la base de données
python manage.py makemigrations
python manage.py migrate

# 5. Initialiser avec des données de test
python init_db.py

# 6. Créer un superutilisateur (optionnel)
python manage.py createsuperuser

# 7. Lancer le serveur
python manage.py runserver
```

### **Option 2 : Installation avec Docker**

#### Prérequis
- Docker Desktop
- Docker Compose

#### Étapes
```bash
# 1. Cloner le projet
git clone https://github.com/TristanLBD/Django-Projet-1.git
cd "Projet Django 2"

# 2. Lancer avec Docker Compose
docker-compose up --build

# 3. L'application sera accessible sur http://localhost:8000
```

## 📊 Comptes de Test

### **Candidats**
- **testuser** / **testpass123** - Candidat de test

### **Employeurs**
- **techcorp_employer** / **techcorp123** - TechCorp Solutions
- **digital_employer** / **digital123** - Digital Marketing Pro
- **green_employer** / **green123** - Green Energy Plus
- **finance_employer** / **finance123** - Finance Consulting
- **creative_employer** / **creative123** - Creative Design Studio

### **Administration**
 - **admin** / **admin123**
- Ou créer manuellement : `python manage.py createsuperuser`

## 🌐 Utilisation

### **Accès à l'Application**
- **Application** : http://localhost:8000
- **Administration** : http://localhost:8000/admin

### **Fonctionnalités Principales**

#### **Candidats**
1. Créer un compte ou se connecter
2. Parcourir les offres d'emploi
3. Postuler avec une lettre de motivation
4. Suivre l'état des candidatures

#### **Employeurs**
1. Se connecter avec un compte employeur
2. Gérer le profil de l'entreprise
3. Publier des offres d'emploi
4. Consulter et traiter les candidatures

#### **Administrateurs**
1. Accéder à l'interface d'administration
2. Gérer les utilisateurs et entreprises
3. Utiliser les fonctionnalités d'import/export CSV
4. Consulter les statistiques

## 📁 Structure du Projet

```
Projet Django 2/
├── accounts/                 # Gestion des utilisateurs
├── api/                     # API REST et import/export
├── companies/               # Gestion des entreprises
├── jobs/                    # Offres d'emploi et candidatures
├── job_platform/           # Configuration principale Django
├── templates/              # Templates HTML
├── static/                 # Fichiers statiques
├── media/                  # Fichiers uploadés
├── docker-compose.yml      # Configuration Docker
├── Dockerfile              # Image Docker
├── requirements.txt        # Dépendances Python
├── init_db.py             # Script d'initialisation
└── readme.md              # Ce fichier
```

## 🔌 API

### **Endpoints Disponibles**
- `GET /api/export/applications/today/` - Export CSV des candidatures du jour
- `GET /api/export/applications/all/` - Export CSV de toutes les candidatures
- `POST /api/import/applications/` - Import CSV de candidatures

### **Format CSV**
Le fichier CSV doit contenir les colonnes suivantes :
- `candidate_email`, `candidate_first_name`, `candidate_last_name`
- `job_title`, `company_name`
- `cover_letter`, `status`
- `application_date`

## ⚙️ Configuration

### **Variables d'Environnement (Optionnel)**
Créer un fichier `.env` à la racine :

```env
# Configuration Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuration base de données (optionnel)
DATABASE_URL=postgresql://django:django123@db:5432/france_chomage

# Configuration email (optionnel)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### **Base de Données**
- **Développement local** : SQLite (automatique)
- **Docker** : PostgreSQL (automatique)
- **Production** : Configurable via `DATABASE_URL`

## 🐳 Docker

### **Services**
- **web** : Application Django (port 8000)
- **db** : Base de données PostgreSQL (port 5432)

### **Commandes Utiles**
```bash
# Démarrer
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down

# Reconstruire
docker-compose up --build

# Accéder au shell Django
docker-compose exec web python manage.py shell

# Accéder à PostgreSQL
docker-compose exec db psql -U django -d france_chomage
```

## 🧪 Tests

```bash
# Tests locaux
python manage.py test

# Tests dans Docker
docker-compose exec web python manage.py test
```

## 📈 Déploiement

### **Production avec Docker**
```bash
# 1. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec les valeurs de production

# 2. Déployer
docker-compose -f docker-compose.prod.yml up -d
```

### **Production Classique**
```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Configurer la base de données de production
# 3. Collecter les fichiers statiques
python manage.py collectstatic

# 4. Utiliser un serveur WSGI (Gunicorn, uWSGI)
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

### **Problèmes Courants**

#### **Erreur de connexion à la base de données**
- Vérifier que Docker Desktop est démarré
- Relancer `docker-compose up --build`

#### **Erreur de migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

#### **Problème de permissions**
```bash
# Windows
icacls . /grant Everyone:F /T

# Linux/Mac
chmod -R 755 .
```

### **Contact**
- **Issues** : [GitHub Issues](url-du-repo/issues)
- **Email** : support@france-chomage.fr

## 🎯 Roadmap

- [ ] Interface mobile responsive
- [ ] Système de notifications push
- [ ] Intégration LinkedIn
- [ ] Système de recommandations
- [ ] Analytics avancées
- [ ] API publique complète

---

**Développé avec ❤️ pour simplifier la recherche d'emploi en France**
