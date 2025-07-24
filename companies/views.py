from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from .models import Company, CompanyPhoto
from .forms import CompanyForm, CompanyPhotoForm
from jobs.models import Job


def is_superuser(user):
    """Vérifie si l'utilisateur est un superuser"""
    return user.is_superuser


def company_detail(request, pk):
    """Vue pour afficher le détail d'une entreprise"""
    company = get_object_or_404(Company, pk=pk, is_active=True)

    # Récupérer les offres d'emploi actives de cette entreprise
    jobs = Job.objects.filter(
        company=company,
        is_active=True,
        is_filled=False
    ).order_by('-created_at')

    return render(request, 'companies/company_detail.html', {
        'company': company,
        'jobs': jobs
    })


@login_required
def company_manage(request):
    """Vue pour gérer les entreprises (employeurs)"""
    from companies.utils import is_admin, get_user_companies
    from jobs.models import Application

    # Vérifier les permissions
    if not is_admin(request.user):
        messages.error(request, 'Accès non autorisé.')
        return redirect('employer_dashboard')

    # Récupérer les entreprises selon les permissions
    if is_admin(request.user):
        companies = Company.objects.all()
    else:
        companies = get_user_companies(request.user)

        # Appliquer les filtres
    status = request.GET.get('status')
    company_name = request.GET.get('company_name')
    location = request.GET.get('location')

    if status == 'active':
        companies = companies.filter(is_active=True)
    elif status == 'inactive':
        companies = companies.filter(is_active=False)

    if company_name:
        companies = companies.filter(name__icontains=company_name)

    if location:
        companies = companies.filter(address__icontains=location)

    # Trier par date de création
    companies = companies.order_by('-created_at')

    # Calculer les statistiques
    total_companies = companies.count()
    active_companies = companies.filter(is_active=True).count()

    # Compter les offres d'emploi
    total_jobs = Job.objects.filter(company__in=companies).count()

    # Compter les candidatures
    total_applications = Application.objects.filter(job__company__in=companies).count()

    # Récupérer les secteurs uniques pour les filtres (basé sur le nom pour l'instant)
    sectors = Company.objects.values_list('name', flat=True).distinct().order_by('name')[:10]

    # Ajouter le nombre total de candidatures par entreprise
    for company in companies:
        company.total_applications = Application.objects.filter(job__company=company).count()

    return render(request, 'companies/company_manage.html', {
        'companies': companies,
        'total_companies': total_companies,
        'active_companies': active_companies,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'sectors': sectors,
    })


@login_required
def company_create(request):
    """Vue pour créer une nouvelle entreprise"""
    from companies.utils import is_admin

    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user

            # Si l'utilisateur n'est pas admin, l'assigner comme employeur responsable
            if not is_admin(request.user):
                company.employer = request.user

            company.save()

            messages.success(request, 'Entreprise créée avec succès !')
            return redirect('companies:company_manage')
    else:
        form = CompanyForm()

    return render(request, 'companies/company_form.html', {
        'form': form,
        'title': 'Créer une entreprise'
    })


@login_required
def company_edit(request, pk):
    """Vue pour modifier une entreprise"""
    from companies.utils import is_admin, can_manage_company

    company = get_object_or_404(Company, pk=pk)

    # Vérifier les permissions
    if not is_admin(request.user) and not can_manage_company(request.user, company):
        messages.error(request, 'Vous n\'avez pas les permissions pour modifier cette entreprise.')
        return redirect('companies:company_manage')

    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entreprise modifiée avec succès !')
            return redirect('companies:company_manage')
    else:
        form = CompanyForm(instance=company)

    return render(request, 'companies/company_form.html', {
        'form': form,
        'company': company,
        'title': 'Modifier l\'entreprise'
    })


@login_required
def company_delete(request, pk):
    """Vue pour supprimer une entreprise"""
    from companies.utils import is_admin, can_manage_company

    company = get_object_or_404(Company, pk=pk)

    # Vérifier les permissions
    if not is_admin(request.user) and not can_manage_company(request.user, company):
        messages.error(request, 'Vous n\'avez pas les permissions pour supprimer cette entreprise.')
        return redirect('companies:company_manage')

    if request.method == 'POST':
        company.delete()
        messages.success(request, 'Entreprise supprimée avec succès !')
        return redirect('companies:company_manage')

    return render(request, 'companies/company_confirm_delete.html', {
        'company': company
    })
