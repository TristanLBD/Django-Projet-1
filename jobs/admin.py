from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from .models import Job, Application


class ApplicationInline(admin.TabularInline):
    """
    Inline pour afficher les candidatures d'une offre d'emploi
    """
    model = Application
    extra = 0
    readonly_fields = ['candidate', 'applied_at', 'status']
    fields = ['candidate', 'applied_at', 'status']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les offres d'emploi
    """
    list_display = [
        'title',
        'company',
        'contract_type',
        'location',
        'is_active',
        'is_filled',
        'application_count',
        'created_at'
    ]
    list_filter = [
        'is_active',
        'is_filled',
        'contract_type',
        'experience_level',
        'is_remote',
        'created_at',
        'company'
    ]
    search_fields = ['title', 'description', 'requirements', 'company__name']
    readonly_fields = ['created_at', 'updated_at', 'application_count']
    inlines = [ApplicationInline]

    fieldsets = (
        ('Informations du poste', {
            'fields': ('title', 'company', 'description', 'requirements')
        }),
        ('Détails du contrat', {
            'fields': ('contract_type', 'experience_level', 'salary_min', 'salary_max')
        }),
        ('Localisation', {
            'fields': ('location', 'is_remote')
        }),
        ('Statut', {
            'fields': ('is_active', 'is_filled')
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def application_count(self, obj):
        """Affiche le nombre de candidatures avec un lien"""
        count = obj.applications.count()
        if count > 0:
            url = reverse('admin:jobs_application_changelist') + f'?job__id__exact={obj.id}'
            return format_html('<a href="{}">{} candidature(s)</a>', url, count)
        return "0 candidature"
    application_count.short_description = "Candidatures"

    def save_model(self, request, obj, form, change):
        """Sauvegarde automatique de l'utilisateur créateur"""
        if not change:  # Nouvelle offre
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Filtre les offres selon les permissions"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les candidatures
    """
    list_display = [
        'candidate_name',
        'job_title',
        'company_name',
        'status',
        'applied_at',
        'reviewed_at',
        'resume_link'
    ]
    list_filter = [
        'status',
        'applied_at',
        'reviewed_at',
        'job__company',
        'job__contract_type'
    ]
    search_fields = [
        'candidate__username',
        'candidate__first_name',
        'candidate__last_name',
        'candidate__email',
        'job__title',
        'job__company__name'
    ]
    readonly_fields = [
        'applied_at',
        'reviewed_at',
        'resume_link',
        'cover_letter_preview'
    ]
    actions = ['mark_as_reviewed', 'mark_as_accepted', 'mark_as_rejected']

    fieldsets = (
        ('Candidature', {
            'fields': ('job', 'candidate', 'status')
        }),
        ('Documents', {
            'fields': ('cover_letter', 'resume', 'resume_link', 'cover_letter_preview')
        }),
        ('Évaluation', {
            'fields': ('reviewed_by', 'notes')
        }),
        ('Dates', {
            'fields': ('applied_at', 'reviewed_at'),
            'classes': ('collapse',)
        }),
    )

    def candidate_name(self, obj):
        """Affiche le nom complet du candidat"""
        return obj.candidate.get_full_name() or obj.candidate.username
    candidate_name.short_description = "Candidat"
    candidate_name.admin_order_field = 'candidate__first_name'

    def job_title(self, obj):
        """Affiche le titre du poste avec lien"""
        url = reverse('admin:jobs_job_change', args=[obj.job.id])
        return format_html('<a href="{}">{}</a>', url, obj.job.title)
    job_title.short_description = "Poste"

    def company_name(self, obj):
        """Affiche le nom de l'entreprise"""
        return obj.job.company.name
    company_name.short_description = "Entreprise"
    company_name.admin_order_field = 'job__company__name'

    def resume_link(self, obj):
        """Affiche un lien vers le CV"""
        if obj.resume:
            return format_html('<a href="{}" target="_blank">Télécharger le CV</a>', obj.resume.url)
        return "Aucun CV"
    resume_link.short_description = "CV"

    def cover_letter_preview(self, obj):
        """Affiche un aperçu de la lettre de motivation"""
        if obj.cover_letter:
            preview = obj.cover_letter[:200] + "..." if len(obj.cover_letter) > 200 else obj.cover_letter
            return format_html('<div style="max-height: 100px; overflow-y: auto;">{}</div>', preview)
        return "Aucune lettre de motivation"
    cover_letter_preview.short_description = "Aperçu lettre de motivation"

    def save_model(self, request, obj, form, change):
        """Sauvegarde automatique de l'utilisateur qui examine"""
        if change and 'status' in form.changed_data:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)

    def mark_as_reviewed(self, request, queryset):
        """Action pour marquer les candidatures comme examinées"""
        updated = queryset.update(
            status='REVIEWED',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        messages.success(request, f'{updated} candidature(s) marquée(s) comme examinée(s).')
    mark_as_reviewed.short_description = "Marquer comme examinées"

    def mark_as_accepted(self, request, queryset):
        """Action pour accepter les candidatures"""
        updated = queryset.update(
            status='ACCEPTED',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        messages.success(request, f'{updated} candidature(s) acceptée(s).')
    mark_as_accepted.short_description = "Accepter les candidatures"

    def mark_as_rejected(self, request, queryset):
        """Action pour refuser les candidatures"""
        updated = queryset.update(
            status='REJECTED',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        messages.success(request, f'{updated} candidature(s) refusée(s).')
    mark_as_rejected.short_description = "Refuser les candidatures"

    def get_queryset(self, request):
        """Filtre les candidatures selon les permissions"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(job__created_by=request.user)

    def get_urls(self):
        """Ajoute les URLs personnalisées pour l'export CSV"""
        urls = super().get_urls()
        custom_urls = [
            path(
                'export-csv/',
                self.admin_site.admin_view(self.export_csv),
                name='jobs_application_export_csv',
            ),
        ]
        return custom_urls + urls

    def export_csv(self, request):
        """Vue pour exporter les candidatures en CSV"""
        from django.http import HttpResponse
        import csv
        from datetime import datetime

        # Récupérer les candidatures filtrées
        queryset = self.get_queryset(request)

        # Créer la réponse CSV
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="candidatures_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        # Écrire l'en-tête BOM pour Excel
        response.write('\ufeff')

        # Créer le writer CSV
        writer = csv.writer(response, delimiter=';')

        # Écrire l'en-tête
        writer.writerow([
            'ID Candidature',
            'Date de candidature',
            'Statut',
            'Nom du candidat',
            'Email du candidat',
            'Titre du poste',
            'Entreprise',
            'Type de contrat',
            'Localisation',
            'Date d\'examen',
            'Examiné par',
            'Notes'
        ])

        # Écrire les données
        for application in queryset:
            writer.writerow([
                application.id,
                application.applied_at.strftime('%d/%m/%Y %H:%M'),
                application.get_status_display(),
                application.candidate.get_full_name() or application.candidate.username,
                application.candidate.email,
                application.job.title,
                application.job.company.name,
                application.job.get_contract_type_display(),
                application.job.location,
                application.reviewed_at.strftime('%d/%m/%Y %H:%M') if application.reviewed_at else '',
                application.reviewed_by.get_full_name() if application.reviewed_by else '',
                application.notes or ''
            ])

        return response
