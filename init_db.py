#!/usr/bin/env python
"""
Script d'initialisation de la base de données
Lancez avec: python init_db.py
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.contrib.auth.models import User
from jobs.models import Job, Application
from companies.models import Company, CompanyPhoto
from accounts.models import UserProfile


def init_database():
    """Initialise la base de données avec des données de test"""
    print("🚀 Début de l'initialisation de la base de données...")

    try:
        # Supprimer toutes les données existantes
        print("🗑️  Suppression des données existantes...")
        Application.objects.all().delete()
        Job.objects.all().delete()
        CompanyPhoto.objects.all().delete()
        Company.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        # Créer un utilisateur de test
        print("👤 Création de l'utilisateur de test...")
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
            print("✅ Utilisateur test créé")

        # Créer des employeurs pour chaque entreprise
        print("👔 Création des employeurs...")
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
                print(f"✅ Employeur {data['username']} créé")
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
                'address': '8 Rue du Digital, 69001 Lyon',
                'phone': '04 78 12 34 56',
                'email': 'contact@digitalmarketingpro.fr',
                'website': 'https://digitalmarketingpro.fr',
                'employer': employers[1]
            },
            {
                'name': 'Green Energy Plus',
                'description': 'Entreprise spécialisée dans les énergies renouvelables et l\'efficacité énergétique.',
                'address': '25 Boulevard Vert, 13001 Marseille',
                'phone': '04 91 23 45 67',
                'email': 'contact@greenenergyplus.fr',
                'website': 'https://greenenergyplus.fr',
                'employer': employers[2]
            },
            {
                'name': 'Finance Consulting',
                'description': 'Cabinet de conseil en finance et gestion d\'entreprise.',
                'address': '12 Place de la Finance, 31000 Toulouse',
                'phone': '05 61 34 56 78',
                'email': 'contact@financeconsulting.fr',
                'website': 'https://financeconsulting.fr',
                'employer': employers[3]
            },
            {
                'name': 'Creative Design Studio',
                'description': 'Studio de design créatif spécialisé dans l\'identité visuelle et le branding.',
                'address': '7 Rue de la Créativité, 44000 Nantes',
                'phone': '02 40 12 34 56',
                'email': 'contact@creativedesignstudio.fr',
                'website': 'https://creativedesignstudio.fr',
                'employer': employers[4]
            }
        ]

        # Créer les entreprises
        print("🏢 Création des entreprises...")
        companies = []
        for data in companies_data:
            company, created = Company.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'address': data['address'],
                    'phone': data['phone'],
                    'email': data['email'],
                    'website': data['website'],
                    'is_active': True,
                    'created_by': data['employer']
                }
            )
            if created:
                print(f"✅ Entreprise {data['name']} créée")
            companies.append(company)

        # Données des offres d'emploi
        jobs_data = [
            # TechCorp Solutions
            {
                'title': 'Développeur Full Stack',
                'description': f"Description détaillée pour le poste de Développeur Full Stack chez {companies[0].name}.",
                'requirements': f"Prérequis pour le poste de Développeur Full Stack : expérience requise, compétences techniques, etc.",
                'benefits': 'Télétravail, mutuelle, tickets restaurant',
                'contract_type': 'CDI',
                'experience_level': 'SENIOR',
                'salary_min': 45000,
                'salary_max': 80000,
                'location': 'Paris',
                'is_remote': True,
                'company': companies[0],
                'created_by': employers[0]
            },
            {
                'title': 'Data Scientist',
                'description': f"Description détaillée pour le poste de Data Scientist chez {companies[0].name}.",
                'requirements': f"Prérequis pour le poste de Data Scientist : expérience requise, compétences techniques, etc.",
                'benefits': 'Télétravail, mutuelle, tickets restaurant',
                'contract_type': 'CDI',
                'experience_level': 'EXPERT',
                'salary_min': 45000,
                'salary_max': 80000,
                'location': 'Paris',
                'is_remote': True,
                'company': companies[0],
                'created_by': employers[0]
            },
            {
                'title': 'DevOps Engineer',
                'description': f"Description détaillée pour le poste de DevOps Engineer chez {companies[0].name}.",
                'requirements': f"Prérequis pour le poste de DevOps Engineer : expérience requise, compétences techniques, etc.",
                'benefits': 'Télétravail, mutuelle, tickets restaurant',
                'contract_type': 'CDD',
                'experience_level': 'JUNIOR',
                'salary_min': 35000,
                'salary_max': 55000,
                'location': 'Paris',
                'is_remote': False,
                'company': companies[0],
                'created_by': employers[0]
            },
            {
                'title': 'Product Manager',
                'description': f"Description détaillée pour le poste de Product Manager chez {companies[0].name}.",
                'requirements': f"Prérequis pour le poste de Product Manager : expérience requise, compétences techniques, etc.",
                'benefits': 'Télétravail, mutuelle, tickets restaurant',
                'contract_type': 'CDI',
                'experience_level': 'SENIOR',
                'salary_min': 45000,
                'salary_max': 80000,
                'location': 'Paris',
                'is_remote': True,
                'company': companies[0],
                'created_by': employers[0]
            },

            # Digital Marketing Pro
            {
                'title': 'Marketing Digital Manager',
                'description': f"Description détaillée pour le poste de Marketing Digital Manager chez {companies[1].name}.",
                'requirements': f"Prérequis pour le poste de Marketing Digital Manager : expérience requise, compétences techniques, etc.",
                'benefits': 'Équipe dynamique, formation continue, avantages sociaux',
                'contract_type': 'CDI',
                'experience_level': 'SENIOR',
                'salary_min': 45000,
                'salary_max': 80000,
                'location': 'Paris',
                'is_remote': True,
                'company': companies[1],
                'created_by': employers[1]
            },
            {
                'title': 'SEO Specialist',
                'description': f"Description détaillée pour le poste de SEO Specialist chez {companies[1].name}.",
                'requirements': f"Prérequis pour le poste de SEO Specialist : expérience requise, compétences techniques, etc.",
                'benefits': 'Équipe dynamique, formation continue, avantages sociaux',
                'contract_type': 'CDD',
                'experience_level': 'JUNIOR',
                'salary_min': 35000,
                'salary_max': 55000,
                'location': 'Paris',
                'is_remote': False,
                'company': companies[1],
                'created_by': employers[1]
            },
            {
                'title': 'Social Media Manager',
                'description': f"Description détaillée pour le poste de Social Media Manager chez {companies[1].name}.",
                'requirements': f"Prérequis pour le poste de Social Media Manager : expérience requise, compétences techniques, etc.",
                'benefits': 'Équipe dynamique, formation continue, avantages sociaux',
                'contract_type': 'CDI',
                'experience_level': 'JUNIOR',
                'salary_min': 35000,
                'salary_max': 55000,
                'location': 'Paris',
                'is_remote': True,
                'company': companies[1],
                'created_by': employers[1]
            },

            # Green Energy Plus
            {
                'title': 'Ingénieur Énergies Renouvelables',
                'description': f"Description détaillée pour le poste d'Ingénieur Énergies Renouvelables chez {companies[2].name}.",
                'requirements': f"Prérequis pour le poste d'Ingénieur Énergies Renouvelables : expérience requise, compétences techniques, etc.",
                'benefits': 'Impact environnemental positif, équipe passionnée',
                'contract_type': 'CDI',
                'experience_level': 'SENIOR',
                'salary_min': 45000,
                'salary_max': 80000,
                'location': 'Lyon',
                'is_remote': False,
                'company': companies[2],
                'created_by': employers[2]
            },
            {
                'title': 'Technicien Maintenance',
                'description': f"Description détaillée pour le poste de Technicien Maintenance chez {companies[2].name}.",
                'requirements': f"Prérequis pour le poste de Technicien Maintenance : expérience requise, compétences techniques, etc.",
                'benefits': 'Impact environnemental positif, équipe passionnée',
                'contract_type': 'CDD',
                'experience_level': 'DEBUTANT',
                'salary_min': 35000,
                'salary_max': 55000,
                'location': 'Lyon',
                'is_remote': False,
                'company': companies[2],
                'created_by': employers[2]
            },

            # Finance & Consulting
            {
                'title': 'Consultant Financier',
                'description': f"Description détaillée pour le poste de Consultant Financier chez {companies[3].name}.",
                'requirements': f"Prérequis pour le poste de Consultant Financier : expérience requise, compétences techniques, etc.",
                'benefits': 'Développement de carrière, salaire attractif',
                'contract_type': 'CDI',
                'experience_level': 'EXPERT',
                'salary_min': 45000,
                'salary_max': 80000,
                'location': 'Marseille',
                'is_remote': True,
                'company': companies[3],
                'created_by': employers[3]
            },
            {
                'title': 'Analyste Financier',
                'description': f"Description détaillée pour le poste d'Analyste Financier chez {companies[3].name}.",
                'requirements': f"Prérequis pour le poste d'Analyste Financier : expérience requise, compétences techniques, etc.",
                'benefits': 'Développement de carrière, salaire attractif',
                'contract_type': 'CDI',
                'experience_level': 'JUNIOR',
                'salary_min': 35000,
                'salary_max': 55000,
                'location': 'Marseille',
                'is_remote': False,
                'company': companies[3],
                'created_by': employers[3]
            },

            # Creative Design Studio
            {
                'title': 'Designer UX/UI',
                'description': f"Description détaillée pour le poste de Designer UX/UI chez {companies[4].name}.",
                'requirements': f"Prérequis pour le poste de Designer UX/UI : expérience requise, compétences techniques, etc.",
                'benefits': 'Environnement créatif, projets variés',
                'contract_type': 'CDI',
                'experience_level': 'SENIOR',
                'salary_min': 45000,
                'salary_max': 80000,
                'location': 'Toulouse',
                'is_remote': True,
                'company': companies[4],
                'created_by': employers[4]
            },
            {
                'title': 'Graphiste Créatif',
                'description': f"Description détaillée pour le poste de Graphiste Créatif chez {companies[4].name}.",
                'requirements': f"Prérequis pour le poste de Graphiste Créatif : expérience requise, compétences techniques, etc.",
                'benefits': 'Environnement créatif, projets variés',
                'contract_type': 'CDD',
                'experience_level': 'JUNIOR',
                'salary_min': 35000,
                'salary_max': 55000,
                'location': 'Toulouse',
                'is_remote': False,
                'company': companies[4],
                'created_by': employers[4]
            }
        ]

        # Créer les offres d'emploi
        print("💼 Création des offres d'emploi...")
        for data in jobs_data:
            job, created = Job.objects.get_or_create(
                title=data['title'],
                company=data['company'],
                defaults={
                    'description': data['description'],
                    'requirements': data['requirements'],
                    'benefits': data['benefits'],
                    'contract_type': data['contract_type'],
                    'experience_level': data['experience_level'],
                    'salary_min': data['salary_min'],
                    'salary_max': data['salary_max'],
                    'location': data['location'],
                    'is_remote': data['is_remote'],
                    'is_active': True,
                    'created_by': data['created_by']
                }
            )
            if created:
                print(f"✅ Offre d'emploi {data['title']} créée")

        # Créer quelques candidatures de test
        print("📝 Création de candidatures de test...")
        test_jobs = Job.objects.all()[:5]  # Premières 5 offres
        for job in test_jobs:
            application, created = Application.objects.get_or_create(
                candidate=test_user,
                job=job,
                defaults={
                    'cover_letter': f"Lettre de motivation pour le poste de {job.title} chez {job.company.name}. Je suis très intéressé par cette opportunité et je pense avoir les compétences nécessaires pour ce poste.",
                    'status': 'PENDING'
                }
            )
            if created:
                print(f"✅ Candidature créée pour {job.title}")

        print("\n🎉 Initialisation terminée avec succès !")
        print("\n📋 Comptes créés :")
        print("   👤 testuser / testpass123 (candidat)")
        print("   👔 techcorp_employer / techcorp123 (employeur)")
        print("   👔 digital_employer / digital123 (employeur)")
        print("   👔 green_employer / green123 (employeur)")
        print("   👔 finance_employer / finance123 (employeur)")
        print("   👔 creative_employer / creative123 (employeur)")
        print("   👑 admin / admin123 (administrateur - à créer manuellement)")
        print("\n🚀 Lancez le serveur avec: python manage.py runserver")

    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation : {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    init_database()
