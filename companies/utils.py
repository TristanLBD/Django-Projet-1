from django.contrib.auth.models import User
from .models import Company


def is_employer(user):
    """Vérifie si l'utilisateur est un employeur (gère au moins une entreprise)"""
    if not user.is_authenticated:
        return False
    return user.companies_managed.exists()


def is_admin(user):
    """Vérifie si l'utilisateur est un admin (superuser)"""
    return user.is_authenticated and user.is_superuser


def get_user_companies(user):
    """Retourne les entreprises gérées par l'utilisateur"""
    if is_admin(user):
        return Company.objects.all()
    elif is_employer(user):
        return user.companies_managed.all()
    else:
        return Company.objects.none()


def can_manage_company(user, company):
    """Vérifie si l'utilisateur peut gérer une entreprise spécifique"""
    if is_admin(user):
        return True
    elif is_employer(user):
        return company in user.companies_managed.all()
    return False


def get_employer_stats(user):
    """Retourne les statistiques pour un employeur"""
    if not is_employer(user) and not is_admin(user):
        return {}

    companies = get_user_companies(user)

    # Statistiques des offres
    from jobs.models import Job
    total_jobs = Job.objects.filter(company__in=companies).count()
    active_jobs = Job.objects.filter(company__in=companies, is_active=True, is_filled=False).count()

    # Statistiques des candidatures
    from jobs.models import Application
    total_applications = Application.objects.filter(job__company__in=companies).count()
    pending_applications = Application.objects.filter(
        job__company__in=companies,
        status='PENDING'
    ).count()

    # Candidatures récentes
    recent_applications = Application.objects.filter(
        job__company__in=companies
    ).select_related('job', 'candidate').order_by('-applied_at')[:5]

    return {
        'total_companies': companies.count(),
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'recent_applications': recent_applications,
    }
