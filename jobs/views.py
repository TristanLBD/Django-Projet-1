from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from .models import Job, Application
from .forms import JobForm, ApplicationForm
from companies.models import Company
from companies.utils import is_employer, is_admin, get_user_companies, can_manage_company


def is_superuser(user):
    """Vérifie si l'utilisateur est un superuser"""
    return user.is_superuser


class JobListView:
    """Vue pour afficher la liste des offres d'emploi disponibles"""

    def __init__(self):
        self.template_name = 'jobs/job_list.html'

    def get(self, request):
        # Récupérer les offres actives et non pourvues
        jobs = Job.objects.filter(
            is_active=True,
            is_filled=False
        ).select_related('company').order_by('-created_at')

        # Filtres
        search = request.GET.get('search', '')
        location = request.GET.get('location', '')
        contract_type = request.GET.get('contract_type', '')
        experience_level = request.GET.get('experience_level', '')

        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) |
                Q(company__name__icontains=search) |
                Q(description__icontains=search)
            )

        if location:
            jobs = jobs.filter(location__icontains=location)

        if contract_type:
            jobs = jobs.filter(contract_type=contract_type)

        if experience_level:
            jobs = jobs.filter(experience_level=experience_level)

        context = {
            'jobs': jobs,
            'search': search,
            'location': location,
            'contract_type': contract_type,
            'experience_level': experience_level,
            'contract_types': Job.CONTRACT_TYPES,
            'experience_levels': Job.EXPERIENCE_LEVELS,
        }

        return render(request, self.template_name, context)


def job_list(request):
    """Vue fonction pour la liste des offres d'emploi"""
    view = JobListView()
    return view.get(request)


class JobDetailView:
    """Vue pour afficher le détail d'une offre d'emploi"""

    def __init__(self):
        self.template_name = 'jobs/job_detail.html'

    def get(self, request, pk):
        job = get_object_or_404(Job, pk=pk, is_active=True)

        # Vérifier si l'utilisateur a déjà postulé
        has_applied = False
        if request.user.is_authenticated:
            has_applied = Application.objects.filter(
                job=job,
                candidate=request.user
            ).exists()

        context = {
            'job': job,
            'has_applied': has_applied,
        }

        return render(request, self.template_name, context)


def job_detail(request, pk):
    """Vue fonction pour le détail d'une offre d'emploi"""
    view = JobDetailView()
    return view.get(request, pk)


@login_required
def job_apply(request, pk):
    """Vue pour postuler à une offre d'emploi"""
    job = get_object_or_404(Job, pk=pk, is_active=True, is_filled=False)

    # Vérifier si l'utilisateur a déjà postulé
    if Application.objects.filter(job=job, candidate=request.user).exists():
        messages.error(request, 'Vous avez déjà postulé à cette offre.')
        return redirect('jobs:job_detail', pk=pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.candidate = request.user
            application.save()

            messages.success(request, 'Votre candidature a été envoyée avec succès !')
            return redirect('jobs:my_applications')
    else:
        form = ApplicationForm()

    return render(request, 'jobs/job_apply.html', {
        'job': job,
        'form': form
    })


@login_required
def my_applications(request):
    """Vue pour afficher les candidatures de l'utilisateur"""
    applications = Application.objects.filter(
        candidate=request.user
    ).select_related('job', 'job__company').order_by('-applied_at')

    return render(request, 'jobs/my_applications.html', {
        'applications': applications
    })


@login_required
def job_manage(request):
    """Vue pour gérer les offres d'emploi (employeurs)"""
    # Vérifier les permissions
    if not is_employer(request.user) and not is_admin(request.user):
        messages.error(request, 'Accès refusé. Vous devez être employeur ou administrateur.')
        return redirect('user_dashboard')

    # Obtenir les entreprises gérées par l'utilisateur
    user_companies = get_user_companies(request.user)

    # Filtrer les offres par entreprise
    jobs = Job.objects.filter(company__in=user_companies).select_related('company').order_by('-created_at')

    # Filtres
    status = request.GET.get('status', '')
    company_id = request.GET.get('company', '')
    contract = request.GET.get('contract', '')
    location = request.GET.get('location', '')

    if status == 'active':
        jobs = jobs.filter(is_active=True, is_filled=False)
    elif status == 'inactive':
        jobs = jobs.filter(is_active=False)
    elif status == 'filled':
        jobs = jobs.filter(is_filled=True)

    if company_id:
        jobs = jobs.filter(company_id=company_id)

    if contract:
        jobs = jobs.filter(contract_type=contract)

    if location:
        jobs = jobs.filter(location__icontains=location)

    # Statistiques filtrées par entreprise
    total_jobs = Job.objects.filter(company__in=user_companies).count()
    active_jobs = Job.objects.filter(company__in=user_companies, is_active=True, is_filled=False).count()
    filled_jobs = Job.objects.filter(company__in=user_companies, is_filled=True).count()
    total_applications = Application.objects.filter(job__company__in=user_companies).count()

    return render(request, 'jobs/job_manage.html', {
        'jobs': jobs,
        'companies': user_companies,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'filled_jobs': filled_jobs,
        'total_applications': total_applications,
        'is_admin': is_admin(request.user),
        'is_employer': is_employer(request.user),
    })


@login_required
def job_create(request):
    """Vue pour créer une nouvelle offre d'emploi"""
    # Vérifier les permissions
    if not is_employer(request.user) and not is_admin(request.user):
        messages.error(request, 'Accès refusé. Vous devez être employeur ou administrateur.')
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = JobForm(request.POST, user=request.user)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()

            messages.success(request, 'Offre d\'emploi créée avec succès !')
            return redirect('jobs:job_manage')
    else:
        form = JobForm(user=request.user)

    return render(request, 'jobs/job_form.html', {
        'form': form,
        'title': 'Créer une offre d\'emploi'
    })


@login_required
def job_edit(request, pk):
    """Vue pour modifier une offre d'emploi"""
    # Vérifier les permissions
    if not is_employer(request.user) and not is_admin(request.user):
        messages.error(request, 'Accès refusé. Vous devez être employeur ou administrateur.')
        return redirect('user_dashboard')

    job = get_object_or_404(Job, pk=pk)

    # Vérifier que l'utilisateur peut modifier cette offre
    user_companies = get_user_companies(request.user)
    if job.company not in user_companies:
        messages.error(request, 'Accès refusé. Vous ne pouvez modifier que les offres de vos entreprises.')
        return redirect('jobs:job_manage')

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Offre d\'emploi modifiée avec succès !')
            return redirect('jobs:job_manage')
    else:
        form = JobForm(instance=job, user=request.user)

    return render(request, 'jobs/job_form.html', {
        'form': form,
        'job': job,
        'title': 'Modifier l\'offre d\'emploi'
    })


@login_required
def job_delete(request, pk):
    """Vue pour supprimer une offre d'emploi"""
    # Vérifier les permissions
    if not is_employer(request.user) and not is_admin(request.user):
        messages.error(request, 'Accès refusé. Vous devez être employeur ou administrateur.')
        return redirect('user_dashboard')

    job = get_object_or_404(Job, pk=pk)

    # Vérifier que l'utilisateur peut supprimer cette offre
    user_companies = get_user_companies(request.user)
    if job.company not in user_companies:
        messages.error(request, 'Accès refusé. Vous ne pouvez supprimer que les offres de vos entreprises.')
        return redirect('jobs:job_manage')

    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Offre d\'emploi supprimée avec succès !')
        return redirect('jobs:job_manage')

    return render(request, 'jobs/job_confirm_delete.html', {
        'job': job
    })


@login_required
def application_list(request):
    """Vue pour afficher toutes les candidatures (employeurs)"""
    # Vérifier les permissions
    if not is_employer(request.user) and not is_admin(request.user):
        messages.error(request, 'Accès refusé. Vous devez être employeur ou administrateur.')
        return redirect('dashboard')

    # Obtenir les entreprises gérées par l'utilisateur
    user_companies = get_user_companies(request.user)

    # Filtrer les candidatures par entreprise
    applications = Application.objects.filter(
        job__company__in=user_companies
    ).select_related(
        'job', 'job__company', 'candidate', 'candidate__profile'
    ).order_by('-applied_at')

    # Filtres
    status = request.GET.get('status', '')
    job_id = request.GET.get('job', '')
    company_id = request.GET.get('company', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if status:
        applications = applications.filter(status=status)

    if job_id:
        applications = applications.filter(job_id=job_id)

    if company_id:
        applications = applications.filter(job__company_id=company_id)

    if date_from:
        applications = applications.filter(applied_at__gte=date_from)

    if date_to:
        applications = applications.filter(applied_at__lte=date_to)

    # Statistiques filtrées par entreprise
    total_applications = Application.objects.filter(job__company__in=user_companies).count()
    pending_count = Application.objects.filter(job__company__in=user_companies, status='PENDING').count()
    reviewed_count = Application.objects.filter(job__company__in=user_companies, status='REVIEWED').count()
    accepted_count = Application.objects.filter(job__company__in=user_companies, status='ACCEPTED').count()

    # Liste des offres pour le filtre (filtrées par entreprise)
    jobs = Job.objects.filter(company__in=user_companies).order_by('title')

    return render(request, 'jobs/application_list.html', {
        'applications': applications,
        'jobs': jobs,
        'user_companies': user_companies,
        'total_applications': total_applications,
        'pending_count': pending_count,
        'reviewed_count': reviewed_count,
        'accepted_count': accepted_count,
        'status_choices': Application.STATUS_CHOICES,
        'is_admin': is_admin(request.user),
        'is_employer': is_employer(request.user),
    })


@login_required
def application_detail(request, pk):
    """Vue pour afficher le détail d'une candidature (employeurs)"""
    application = get_object_or_404(Application, pk=pk)

    return render(request, 'jobs/application_detail.html', {
        'application': application
    })


@login_required
def application_review(request, pk):
    """Vue pour examiner une candidature (employeurs)"""
    application = get_object_or_404(Application, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')

        if new_status in dict(Application.STATUS_CHOICES):
            application.status = new_status
            application.notes = notes
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()

            messages.success(request, 'Candidature examinée avec succès !')
            return redirect('jobs:application_detail', pk=pk)

    return render(request, 'jobs/application_review.html', {
        'application': application,
        'status_choices': Application.STATUS_CHOICES,
    })
