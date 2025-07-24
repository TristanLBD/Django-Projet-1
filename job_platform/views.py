from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.utils import timezone
from jobs.models import Job, Application
from companies.models import Company, CompanyPhoto
from accounts.models import UserProfile
from companies.utils import is_employer, is_admin, get_employer_stats, get_user_companies


def home(request):
    """Vue pour la page d'accueil"""
    if request.user.is_authenticated:
        # Rediriger selon le type d'utilisateur
        if is_admin(request.user):
            return redirect('admin_dashboard')
        elif is_employer(request.user):
            return redirect('employer_dashboard')
        else:
            return redirect('user_dashboard')

    # Afficher quelques offres d'emploi récentes pour les visiteurs
    recent_jobs = Job.objects.filter(is_active=True, is_filled=False).select_related('company').order_by('-created_at')[:6]

    return render(request, 'home.html', {
        'recent_jobs': recent_jobs
    })


def user_dashboard(request):
    """Vue pour le dashboard candidat"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    # Rediriger les employeurs et admins vers leurs dashboards respectifs
    if is_admin(request.user):
        return redirect('admin_dashboard')
    elif is_employer(request.user):
        return redirect('employer_dashboard')

    # Obtenir les candidatures de l'utilisateur
    user_applications = Application.objects.filter(candidate=request.user).select_related('job', 'job__company').order_by('-applied_at')[:5]

    # Obtenir les offres d'emploi récentes
    recent_jobs = Job.objects.filter(is_active=True, is_filled=False).select_related('company').order_by('-created_at')[:6]

    return render(request, 'user_dashboard.html', {
        'user': request.user,
        'user_applications': user_applications,
        'recent_jobs': recent_jobs
    })


def employer_dashboard(request):
    """Vue pour le dashboard employeur (filtré par entreprise)"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    # Rediriger les admins vers le dashboard admin
    if is_admin(request.user):
        return redirect('admin_dashboard')

    # Vérifier si l'utilisateur est employeur
    if not is_employer(request.user):
        messages.error(request, 'Accès refusé. Vous devez être employeur.')
        return redirect('user_dashboard')

    # Obtenir les statistiques filtrées par entreprise
    stats = get_employer_stats(request.user)

    # Obtenir les entreprises gérées par l'utilisateur
    user_companies = get_user_companies(request.user)

    return render(request, 'employer_dashboard.html', {
        'user': request.user,
        'user_companies': user_companies,
        'is_employer': True,
        **stats
    })


def admin_dashboard(request):
    """Vue pour le dashboard administrateur (toutes les données)"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    # Vérifier si l'utilisateur est admin
    if not is_admin(request.user):
        messages.error(request, 'Accès refusé. Vous devez être administrateur.')
        if is_employer(request.user):
            return redirect('employer_dashboard')
        else:
            return redirect('user_dashboard')

    # Statistiques globales
    total_jobs = Job.objects.count()
    total_applications = Application.objects.count()
    total_companies = Company.objects.count()
    total_users = User.objects.filter(is_superuser=False).count()

    # Candidatures récentes
    recent_applications = Application.objects.select_related('job', 'job__company', 'candidate').order_by('-applied_at')[:10]

    # Offres d'emploi récentes
    recent_jobs = Job.objects.select_related('company').order_by('-created_at')[:10]

    # Entreprises récentes
    recent_companies = Company.objects.order_by('-created_at')[:5]

    return render(request, 'admin_dashboard.html', {
        'user': request.user,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'total_companies': total_companies,
        'total_users': total_users,
        'recent_applications': recent_applications,
        'recent_jobs': recent_jobs,
        'recent_companies': recent_companies,
        'is_admin': True
    })


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

        # Créer des employeurs pour chaque entreprise
        employers_data = [
            {
                'username': 'techcorp_employer',
                'email': 'employer@techcorp.fr',
                'first_name': 'Jean',
                'last_name': 'TechCorp',
                'password': 'techcorp123'
            },
            {
                'username': 'digital_employer',
                'email': 'employer@digitalmarketingpro.fr',
                'first_name': 'Marie',
                'last_name': 'Digital',
                'password': 'digital123'
            },
            {
                'username': 'green_employer',
                'email': 'employer@greenenergyplus.fr',
                'first_name': 'Pierre',
                'last_name': 'Green',
                'password': 'green123'
            },
            {
                'username': 'finance_employer',
                'email': 'employer@financeconsulting.fr',
                'first_name': 'Sophie',
                'last_name': 'Finance',
                'password': 'finance123'
            },
            {
                'username': 'creative_employer',
                'email': 'employer@creativedesignstudio.fr',
                'first_name': 'Lucas',
                'last_name': 'Creative',
                'password': 'creative123'
            }
        ]

        # Créer les employeurs
        employers = []
        for data in employers_data:
            employer, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'is_staff': True
                }
            )
            if created:
                employer.set_password(data['password'])
                employer.save()
            employers.append(employer)

        # Données des entreprises
        companies_data = [
            {
                'name': 'TechCorp Solutions',
                'description': 'Entreprise leader dans le développement de solutions technologiques innovantes.',
                'address': '15 Avenue de l\'Innovation, 75001 Paris',
                'phone': '01 42 34 56 78',
                'email': 'contact@techcorp.fr',
                'website': 'https://techcorp.fr',
                'employer': employers[0]
            },
            {
                'name': 'Digital Marketing Pro',
                'description': 'Agence de marketing digital spécialisée dans la transformation numérique.',
                'address': '28 Rue du Commerce, 75015 Paris',
                'phone': '01 45 67 89 12',
                'email': 'info@digitalmarketingpro.fr',
                'website': 'https://digitalmarketingpro.fr',
                'employer': employers[1]
            },
            {
                'name': 'Green Energy Plus',
                'description': 'Entreprise spécialisée dans les énergies renouvelables et l\'efficacité énergétique.',
                'address': '7 Boulevard de l\'Écologie, 69001 Lyon',
                'phone': '04 78 12 34 56',
                'email': 'contact@greenenergyplus.fr',
                'website': 'https://greenenergyplus.fr',
                'employer': employers[2]
            },
            {
                'name': 'Finance & Consulting',
                'description': 'Cabinet de conseil financier et stratégique pour PME et startups.',
                'address': '42 Rue de la Finance, 13001 Marseille',
                'phone': '04 91 23 45 67',
                'email': 'contact@financeconsulting.fr',
                'website': 'https://financeconsulting.fr',
                'employer': employers[3]
            },
            {
                'name': 'Creative Design Studio',
                'description': 'Studio de design créatif spécialisé dans l\'identité visuelle et l\'UX/UI.',
                'address': '3 Place des Arts, 31000 Toulouse',
                'phone': '05 61 34 56 78',
                'email': 'hello@creativedesignstudio.fr',
                'website': 'https://creativedesignstudio.fr',
                'employer': employers[4]
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
                created_by=request.user,
                employer=data['employer']
            )
            companies.append(company)

        # Données des offres d'emploi
        jobs_data = [
            # TechCorp Solutions
            {'title': 'Développeur Full Stack', 'contract': 'CDI', 'level': 'SENIOR', 'location': 'Paris', 'remote': True, 'company': companies[0]},
            {'title': 'Data Scientist', 'contract': 'CDI', 'level': 'EXPERT', 'location': 'Paris', 'remote': True, 'company': companies[0]},
            {'title': 'DevOps Engineer', 'contract': 'CDD', 'level': 'JUNIOR', 'location': 'Paris', 'remote': False, 'company': companies[0]},
            {'title': 'Product Manager', 'contract': 'CDI', 'level': 'SENIOR', 'location': 'Paris', 'remote': True, 'company': companies[0]},

            # Digital Marketing Pro
            {'title': 'Marketing Digital Manager', 'contract': 'CDI', 'level': 'SENIOR', 'location': 'Paris', 'remote': True, 'company': companies[1]},
            {'title': 'SEO Specialist', 'contract': 'CDD', 'level': 'JUNIOR', 'location': 'Paris', 'remote': False, 'company': companies[1]},
            {'title': 'Social Media Manager', 'contract': 'CDI', 'level': 'JUNIOR', 'location': 'Paris', 'remote': True, 'company': companies[1]},

            # Green Energy Plus
            {'title': 'Ingénieur Énergies Renouvelables', 'contract': 'CDI', 'level': 'SENIOR', 'location': 'Lyon', 'remote': False, 'company': companies[2]},
            {'title': 'Technicien Maintenance', 'contract': 'CDD', 'level': 'DEBUTANT', 'location': 'Lyon', 'remote': False, 'company': companies[2]},

            # Finance & Consulting
            {'title': 'Consultant Financier', 'contract': 'CDI', 'level': 'EXPERT', 'location': 'Marseille', 'remote': True, 'company': companies[3]},
            {'title': 'Analyste Financier', 'contract': 'CDI', 'level': 'JUNIOR', 'location': 'Marseille', 'remote': False, 'company': companies[3]},

            # Creative Design Studio
            {'title': 'Designer UX/UI', 'contract': 'CDI', 'level': 'SENIOR', 'location': 'Toulouse', 'remote': True, 'company': companies[4]},
            {'title': 'Graphiste Créatif', 'contract': 'CDD', 'level': 'JUNIOR', 'location': 'Toulouse', 'remote': False, 'company': companies[4]},
        ]

        # Créer les offres d'emploi
        for data in jobs_data:
            Job.objects.create(
                title=data['title'],
                company=data['company'],
                description=f"Description détaillée pour le poste de {data['title']} chez {data['company'].name}.",
                requirements=f"Prérequis pour le poste de {data['title']} : expérience requise, compétences techniques, etc.",
                contract_type=data['contract'],
                experience_level=data['level'],
                salary_min=35000 if data['level'] in ['JUNIOR', 'DEBUTANT'] else 45000,
                salary_max=55000 if data['level'] in ['JUNIOR', 'DEBUTANT'] else 80000,
                location=data['location'],
                is_remote=data['remote'],
                created_by=request.user
            )

        # Créer quelques candidatures de test
        test_user = User.objects.get(username='testuser')
        for job in Job.objects.all()[:5]:  # Premières 5 offres
            Application.objects.create(
                job=job,
                candidate=test_user,
                cover_letter=f"Lettre de motivation pour le poste de {job.title} chez {job.company.name}. Je suis très intéressé par cette opportunité et je pense avoir les compétences nécessaires pour ce poste.",
                resume=None,  # Pas de CV pour les tests
                status='PENDING'
            )

        return HttpResponse("Base de données initialisée avec succès !<br><br>"
                          "<strong>Comptes employeurs créés :</strong><br>"
                          "• techcorp_employer / techcorp123<br>"
                          "• digital_employer / digital123<br>"
                          "• green_employer / green123<br>"
                          "• finance_employer / finance123<br>"
                          "• creative_employer / creative123<br><br>"
                          "• testuser / testpass123 (candidat)<br>"
                          "• admin / admin123 (administrateur)")

    except Exception as e:
        return HttpResponse(f"Erreur lors de l'initialisation : {str(e)}", status=500)
