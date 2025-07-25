from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from .models import Job, Application
from .forms import JobForm, ApplicationForm
from companies.models import Company
from companies.utils import is_employer, is_admin, get_user_companies, can_manage_company


class JobListView(ListView):
    """Vue pour afficher la liste des offres d'emploi disponibles"""
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        queryset = Job.objects.filter(
            is_active=True,
            is_filled=False
        ).select_related('company').order_by('-created_at')

        # Filtres
        search = self.request.GET.get('search', '')
        location = self.request.GET.get('location', '')
        contract_type = self.request.GET.get('contract_type', '')
        experience_level = self.request.GET.get('experience_level', '')

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(company__name__icontains=search) |
                Q(description__icontains=search)
            )

        if location:
            queryset = queryset.filter(location__icontains=location)

        if contract_type:
            queryset = queryset.filter(contract_type=contract_type)

        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['location'] = self.request.GET.get('location', '')
        context['contract_type'] = self.request.GET.get('contract_type', '')
        context['experience_level'] = self.request.GET.get('experience_level', '')
        context['contract_types'] = Job.CONTRACT_TYPES
        context['experience_levels'] = Job.EXPERIENCE_LEVELS
        return context


class JobDetailView(DetailView):
    """Vue pour afficher le détail d'une offre d'emploi"""
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'

    def get_queryset(self):
        return Job.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Vérifier si l'utilisateur a déjà postulé
        context['has_applied'] = False
        if self.request.user.is_authenticated:
            context['has_applied'] = Application.objects.filter(
                job=self.object,
                candidate=self.request.user
            ).exists()
        return context


class JobApplyView(LoginRequiredMixin, View):
    """Vue pour postuler à une offre d'emploi"""
    template_name = 'jobs/job_apply.html'

    def get(self, request, pk):
        job = get_object_or_404(Job, pk=pk, is_active=True)

        # Vérifier si l'utilisateur a déjà postulé
        if Application.objects.filter(job=job, candidate=request.user).exists():
            messages.warning(request, 'Vous avez déjà postulé à cette offre.')
            return redirect('jobs:job_detail', pk=pk)

        form = ApplicationForm()
        return render(request, self.template_name, {
            'form': form,
            'job': job
        })

    def post(self, request, pk):
        job = get_object_or_404(Job, pk=pk, is_active=True)

        # Vérifier si l'utilisateur a déjà postulé
        if Application.objects.filter(job=job, candidate=request.user).exists():
            messages.warning(request, 'Vous avez déjà postulé à cette offre.')
            return redirect('jobs:job_detail', pk=pk)

        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.candidate = request.user
            application.save()

            messages.success(request, 'Votre candidature a été envoyée avec succès !')
            return redirect('jobs:job_detail', pk=pk)

        return render(request, self.template_name, {
            'form': form,
            'job': job
        })


class MyApplicationsView(LoginRequiredMixin, ListView):
    """Vue pour afficher les candidatures de l'utilisateur"""
    model = Application
    template_name = 'jobs/my_applications.html'
    context_object_name = 'applications'

    def get_queryset(self):
        return Application.objects.filter(candidate=self.request.user).select_related('job', 'job__company').order_by('-applied_at')


class JobManageView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vue pour gérer les offres d'emploi (employeurs)"""
    model = Job
    template_name = 'jobs/job_manage.html'
    context_object_name = 'jobs'

    def test_func(self):
        return is_admin(self.request.user) or is_employer(self.request.user)

    def get_queryset(self):
        if is_admin(self.request.user):
            queryset = Job.objects.all()
        else:
            user_companies = get_user_companies(self.request.user)
            queryset = Job.objects.filter(company__in=user_companies)

        # Appliquer les filtres
        status = self.request.GET.get('status')
        company = self.request.GET.get('company')
        contract_type = self.request.GET.get('contract_type')

        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        elif status == 'filled':
            queryset = queryset.filter(is_filled=True)
        elif status == 'open':
            queryset = queryset.filter(is_filled=False)

        if company:
            queryset = queryset.filter(company__name__icontains=company)

        if contract_type:
            queryset = queryset.filter(contract_type=contract_type)

        return queryset.select_related('company').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        jobs = context['jobs']

        # Calculer les statistiques
        context['total_jobs'] = jobs.count()
        context['active_jobs'] = jobs.filter(is_active=True).count()
        context['filled_jobs'] = jobs.filter(is_filled=True).count()
        context['total_applications'] = Application.objects.filter(job__in=jobs).count()

        # Récupérer les entreprises pour les filtres
        if is_admin(self.request.user):
            context['companies'] = Company.objects.all()
        else:
            context['companies'] = get_user_companies(self.request.user)

        context['contract_types'] = Job.CONTRACT_TYPES

        return context


class JobCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Vue pour créer une nouvelle offre d'emploi"""
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('jobs:job_manage')

    def test_func(self):
        return is_admin(self.request.user) or is_employer(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Créer une offre d\'emploi'
        return context

    def form_valid(self, form):
        job = form.save(commit=False)
        job.created_by = self.request.user
        job.save()
        messages.success(self.request, 'Offre d\'emploi créée avec succès !')
        return super().form_valid(form)


class JobEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vue pour modifier une offre d'emploi"""
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('jobs:job_manage')

    def test_func(self):
        job = self.get_object()
        return is_admin(self.request.user) or can_manage_company(self.request.user, job.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier l\'offre d\'emploi'
        context['job'] = self.object
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Offre d\'emploi modifiée avec succès !')
        return super().form_valid(form)


class JobDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vue pour supprimer une offre d'emploi"""
    model = Job
    template_name = 'jobs/job_confirm_delete.html'
    success_url = reverse_lazy('jobs:job_manage')

    def test_func(self):
        job = self.get_object()
        return is_admin(self.request.user) or can_manage_company(self.request.user, job.company)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Offre d\'emploi supprimée avec succès !')
        return super().delete(request, *args, **kwargs)


class ApplicationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vue pour afficher la liste des candidatures (employeurs)"""
    model = Application
    template_name = 'jobs/application_list.html'
    context_object_name = 'applications'

    def test_func(self):
        return is_admin(self.request.user) or is_employer(self.request.user)

    def get_queryset(self):
        if is_admin(self.request.user):
            queryset = Application.objects.all()
        else:
            user_companies = get_user_companies(self.request.user)
            queryset = Application.objects.filter(job__company__in=user_companies)

        # Appliquer les filtres
        status = self.request.GET.get('status')
        job = self.request.GET.get('job')
        company = self.request.GET.get('company')

        if status:
            queryset = queryset.filter(status=status)

        if job:
            queryset = queryset.filter(job__title__icontains=job)

        if company:
            queryset = queryset.filter(job__company__name__icontains=company)

        return queryset.select_related('job', 'job__company', 'candidate').order_by('-applied_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        applications = context['applications']

        # Calculer les statistiques
        context['total_applications'] = applications.count()
        context['pending_applications'] = applications.filter(status='pending').count()
        context['accepted_applications'] = applications.filter(status='accepted').count()
        context['rejected_applications'] = applications.filter(status='rejected').count()

        # Récupérer les offres d'emploi pour les filtres
        if is_admin(self.request.user):
            context['jobs'] = Job.objects.all()
            context['companies'] = Company.objects.all()
        else:
            user_companies = get_user_companies(self.request.user)
            context['jobs'] = Job.objects.filter(company__in=user_companies)
            context['companies'] = user_companies

        return context


class ApplicationDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Vue pour afficher le détail d'une candidature"""
    model = Application
    template_name = 'jobs/application_detail.html'
    context_object_name = 'application'

    def test_func(self):
        application = self.get_object()
        return (is_admin(self.request.user) or
                is_employer(self.request.user) or
                application.candidate == self.request.user)


class ApplicationReviewView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vue pour examiner une candidature (employeurs)"""
    model = Application
    template_name = 'jobs/application_review.html'
    fields = ['status', 'notes']
    success_url = reverse_lazy('jobs:application_list')

    def test_func(self):
        application = self.get_object()
        return is_admin(self.request.user) or can_manage_company(self.request.user, application.job.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = self.object
        return context

    def form_valid(self, form):
        old_status = self.object.status
        response = super().form_valid(form)

        if old_status != form.instance.status:
            messages.success(self.request, f'Statut de la candidature mis à jour : {form.instance.get_status_display()}')

        return response
