from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db import connection
from companies.models import Company, CompanyPhoto
from jobs.models import Job, Application
from accounts.models import UserProfile
from django.utils import timezone
from datetime import timedelta
import random


def home(request):
    return HttpResponse("""
    <h1>Plateforme de Dépôt de Candidature</h1>
    <p>Bienvenue sur la plateforme de gestion des candidatures d'emploi.</p>
    <ul>
        <li><a href="/admin/">Administration</a></li>
        <li><a href="/api/export/applications/today/">API Export CSV</a></li>
        <li><a href="/admin/initdb/">Initialiser la base de données</a></li>
    </ul>
    """)


def init_db(request):
    # Vérifier si l'utilisateur est superuser
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponse("Accès refusé. Superuser requis.", status=403)

    try:
        # Supprimer toutes les données existantes
        Application.objects.all().delete()
        Job.objects.all().delete()
        CompanyPhoto.objects.all().delete()
        Company.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        # Créer un utilisateur de test
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'is_staff': True
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()

        # Données des entreprises
        companies_data = [
            {
                'name': 'TechCorp Solutions',
                'description': 'Entreprise leader dans le développement de solutions technologiques innovantes.',
                'address': '15 Avenue de l\'Innovation, 75001 Paris',
                'phone': '01 42 34 56 78',
                'email': 'contact@techcorp.fr',
                'website': 'https://techcorp.fr'
            },
            {
                'name': 'Digital Marketing Pro',
                'description': 'Agence de marketing digital spécialisée dans la transformation numérique.',
                'address': '28 Rue du Commerce, 75015 Paris',
                'phone': '01 45 67 89 12',
                'email': 'info@digitalmarketingpro.fr',
                'website': 'https://digitalmarketingpro.fr'
            },
            {
                'name': 'Green Energy Plus',
                'description': 'Entreprise spécialisée dans les énergies renouvelables et l\'efficacité énergétique.',
                'address': '7 Boulevard de l\'Écologie, 69001 Lyon',
                'phone': '04 78 12 34 56',
                'email': 'contact@greenenergyplus.fr',
                'website': 'https://greenenergyplus.fr'
            },
            {
                'name': 'Finance & Consulting',
                'description': 'Cabinet de conseil financier et stratégique pour PME et startups.',
                'address': '42 Rue de la Finance, 13001 Marseille',
                'phone': '04 91 23 45 67',
                'email': 'contact@financeconsulting.fr',
                'website': 'https://financeconsulting.fr'
            },
            {
                'name': 'Creative Design Studio',
                'description': 'Studio de design créatif spécialisé dans l\'identité visuelle et l\'UX/UI.',
                'address': '3 Place des Arts, 31000 Toulouse',
                'phone': '05 61 34 56 78',
                'email': 'hello@creativedesignstudio.fr',
                'website': 'https://creativedesignstudio.fr'
            }
        ]

        # Créer les entreprises
        companies = []
        for data in companies_data:
            company = Company.objects.create(
                name=data['name'],
                description=data['description'],
                address=data['address'],
                phone=data['phone'],
                email=data['email'],
                website=data['website'],
                created_by=request.user
            )
            companies.append(company)

        # Données des offres d'emploi
        jobs_data = [
            # TechCorp Solutions
            {'title': 'Développeur Full Stack', 'contract': 'CDI', 'level': 'SENIOR', 'location': 'Paris', 'remote': True},
            {'title': 'Data Scientist', 'contract': 'CDI', 'level': 'EXPERT', 'location': 'Paris', 'remote': True},
            {'title': 'DevOps Engineer', 'contract': 'CDD', 'level': 'JUNIOR', 'location': 'Paris', 'remote': False},
            {'title': 'Product Manager', 'contract': 'CDI', 'level': 'SENIOR', 'location': 'Paris', 'remote': True},
            {'title': 'UX/UI Designer', 'contract': 'STAGE', 'level': 'DEBUTANT', 'location': 'Paris', 'remote': False},

            # Digital Marketing Pro
            {'title': 'Chef de Projet Marketing', 'contract': 'CDI', 'level': 'SENIOR', 'location': 'Paris', 'remote': True},
            {'title': 'Community Manager', 'contract': 'CDD', 'level': 'JUNIOR', 'location': 'Paris', 'remote': True},
            {'title': 'Analyste SEO', 'contract': 'CDI', 'level': 'JUNIOR', 'location': 'Paris', 'remote': False},
            {'title': 'Graphiste', 'contract': 'ALTERNANCE', 'level': 'DEBUTANT', 'location': 'Paris', 'remote': False},
            {'title': 'Responsable Communication', 'contract': 'CDI', 'level': 'SENIOR', 'location': 'Paris', 'remote': True},

            # Green Energy Plus
            {'title': 'Ingénieur Énergies Renouvelables', 'contract': 'CDI', 'level': 'SENIOR', 'location': 'Lyon', 'remote': False},
            {'title': 'Technicien Maintenance', 'contract': 'CDI', 'level': 'JUNIOR', 'location': 'Lyon', 'remote': False},
            {'title': 'Chargé d\'Affaires', 'contract': 'CDD', 'level': 'JUNIOR', 'location': 'Lyon', 'remote': True},
            {'title': 'Stagiaire R&D', 'contract': 'STAGE', 'level': 'DEBUTANT', 'location': 'Lyon', 'remote': False},
            {'title': 'Responsable Projet', 'contract': 'CDI', 'level': 'EXPERT', 'location': 'Lyon', 'remote': True},

            # Finance & Consulting
            {'title': 'Consultant Financier', 'contract': 'CDI', 'level': 'SENIOR', 'location': 'Marseille', 'remote': True},
            {'title': 'Analyste Financier', 'contract': 'CDD', 'level': 'JUNIOR', 'location': 'Marseille', 'remote': False},
            {'title': 'Chargé de Clientèle', 'contract': 'CDI', 'level': 'JUNIOR', 'location': 'Marseille', 'remote': False},
            {'title': 'Stagiaire Audit', 'contract': 'STAGE', 'level': 'DEBUTANT', 'location': 'Marseille', 'remote': False},
            {'title': 'Directeur Financier', 'contract': 'CDI', 'level': 'EXPERT', 'location': 'Marseille', 'remote': True},

            # Creative Design Studio
            {'title': 'Designer Graphique', 'contract': 'CDI', 'level': 'SENIOR', 'location': 'Toulouse', 'remote': True},
            {'title': 'UX Designer', 'contract': 'CDD', 'level': 'JUNIOR', 'location': 'Toulouse', 'remote': True},
            {'title': 'Motion Designer', 'contract': 'CDI', 'level': 'JUNIOR', 'location': 'Toulouse', 'remote': False},
            {'title': 'Stagiaire Design', 'contract': 'STAGE', 'level': 'DEBUTANT', 'location': 'Toulouse', 'remote': False},
            {'title': 'Directeur Artistique', 'contract': 'CDI', 'level': 'EXPERT', 'location': 'Toulouse', 'remote': True}
        ]

        # Créer les offres d'emploi
        jobs = []
        for i, job_data in enumerate(jobs_data):
            company = companies[i // 5]  # 5 jobs par entreprise
            job = Job.objects.create(
                title=job_data['title'],
                company=company,
                description=f"Description détaillée du poste {job_data['title']} chez {company.name}.",
                requirements=f"Prérequis pour le poste {job_data['title']} : expérience, compétences, formation.",
                contract_type=job_data['contract'],
                experience_level=job_data['level'],
                location=job_data['location'],
                is_remote=job_data['remote'],
                created_by=request.user
            )
            jobs.append(job)

        # Créer quelques candidatures de test
        candidates_data = [
            {'username': 'candidat1', 'email': 'candidat1@example.com', 'first_name': 'Jean', 'last_name': 'Dupont'},
            {'username': 'candidat2', 'email': 'candidat2@example.com', 'first_name': 'Marie', 'last_name': 'Martin'},
            {'username': 'candidat3', 'email': 'candidat3@example.com', 'first_name': 'Pierre', 'last_name': 'Durand'},
            {'username': 'candidat4', 'email': 'candidat4@example.com', 'first_name': 'Sophie', 'last_name': 'Leroy'},
            {'username': 'candidat5', 'email': 'candidat5@example.com', 'first_name': 'Lucas', 'last_name': 'Moreau'},
        ]

        candidates = []
        for data in candidates_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name']
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            candidates.append(user)

        # Créer des candidatures (en s'assurant qu'un candidat ne postule qu'une fois par offre)
        statuses = ['PENDING', 'REVIEWED', 'ACCEPTED', 'REJECTED']
        applications_created = 0
        max_attempts = 100  # Éviter une boucle infinie

        for attempt in range(max_attempts):
            if applications_created >= 15:  # On veut 15 candidatures
                break

            job = random.choice(jobs)
            candidate = random.choice(candidates)
            status = random.choice(statuses)

            # Vérifier si cette candidature existe déjà
            if not Application.objects.filter(job=job, candidate=candidate).exists():
                application = Application.objects.create(
                    job=job,
                    candidate=candidate,
                    cover_letter=f"Lettre de motivation pour le poste {job.title}",
                    status=status
                )

                # Si le statut n'est pas en attente, ajouter des dates de review
                if status != 'PENDING':
                    application.reviewed_at = timezone.now() - timedelta(days=random.randint(1, 30))
                    application.reviewed_by = request.user
                    application.save()

                applications_created += 1

        return HttpResponse(f"""
        <h1>Base de données initialisée avec succès !</h1>
        <p>Données créées :</p>
        <ul>
            <li>5 entreprises</li>
            <li>25 offres d'emploi (5 par entreprise)</li>
            <li>5 candidats</li>
            <li>{applications_created} candidatures</li>
        </ul>
        <p><a href="/admin/">Aller à l'administration</a></p>
        <p><a href="/">Retour à l'accueil</a></p>
        """)

    except Exception as e:
        return HttpResponse(f"Erreur lors de l'initialisation : {str(e)}", status=500)
