from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from .models import Company, CompanyPhoto
from .forms import CompanyForm, CompanyPhotoForm
from jobs.models import Job
from .utils import is_admin, get_user_companies, can_manage_company


class CompanyDetailView(DetailView):
    """Vue pour afficher le détail d'une entreprise"""
    model = Company
    template_name = 'companies/company_detail.html'
    context_object_name = 'company'

    def get_queryset(self):
        return Company.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Récupérer les offres d'emploi actives de cette entreprise
        context['jobs'] = Job.objects.filter(
            company=self.object,
            is_active=True,
            is_filled=False
        ).order_by('-created_at')
        return context


class CompanyManageView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vue pour gérer les entreprises (employeurs)"""
    model = Company
    template_name = 'companies/company_manage.html'
    context_object_name = 'companies'

    def test_func(self):
        return is_admin(self.request.user)

    def get_queryset(self):
        queryset = Company.objects.all()

        # Appliquer les filtres
        status = self.request.GET.get('status')
        company_name = self.request.GET.get('company_name')
        location = self.request.GET.get('location')

        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        if company_name:
            queryset = queryset.filter(name__icontains=company_name)

        if location:
            queryset = queryset.filter(address__icontains=location)

        # Trier par date de création
        queryset = queryset.order_by('-created_at')

        # Ajouter le nombre total de candidatures par entreprise
        from jobs.models import Application
        for company in queryset:
            company.total_applications = Application.objects.filter(job__company=company).count()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        companies = context['companies']

        # Calculer les statistiques
        context['total_companies'] = companies.count()
        context['active_companies'] = companies.filter(is_active=True).count()
        context['total_jobs'] = Job.objects.filter(company__in=companies).count()

        from jobs.models import Application
        context['total_applications'] = Application.objects.filter(job__company__in=companies).count()

        # Récupérer les secteurs uniques pour les filtres
        context['sectors'] = Company.objects.values_list('name', flat=True).distinct().order_by('name')[:10]

        return context


class CompanyCreateView(LoginRequiredMixin, CreateView):
    """Vue pour créer une nouvelle entreprise"""
    model = Company
    form_class = CompanyForm
    template_name = 'companies/company_form.html'
    success_url = reverse_lazy('companies:company_manage')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Créer une entreprise'
        return context

    def form_valid(self, form):
        company = form.save(commit=False)
        company.created_by = self.request.user

        # Si l'utilisateur n'est pas admin, l'assigner comme employeur responsable
        if not is_admin(self.request.user):
            company.employer = self.request.user

        company.save()
        messages.success(self.request, 'Entreprise créée avec succès !')
        return super().form_valid(form)


class CompanyEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vue pour modifier une entreprise"""
    model = Company
    form_class = CompanyForm
    template_name = 'companies/company_form.html'
    success_url = reverse_lazy('companies:company_manage')

    def test_func(self):
        company = self.get_object()
        return is_admin(self.request.user) or can_manage_company(self.request.user, company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier l\'entreprise'
        context['company'] = self.object
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Entreprise modifiée avec succès !')
        return super().form_valid(form)


class CompanyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vue pour supprimer une entreprise"""
    model = Company
    template_name = 'companies/company_confirm_delete.html'
    success_url = reverse_lazy('companies:company_manage')

    def test_func(self):
        company = self.get_object()
        return is_admin(self.request.user) or can_manage_company(self.request.user, company)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Entreprise supprimée avec succès !')
        return super().delete(request, *args, **kwargs)
