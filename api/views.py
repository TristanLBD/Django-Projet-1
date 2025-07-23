import csv
import io
from datetime import datetime, timezone
from django.http import HttpResponse
from django.utils import timezone as django_timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from jobs.models import Application
from .models import CSVExport


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_applications_csv(request):
    try:
        # Récupérer la date d'aujourd'hui
        today = django_timezone.now().date()

        # Filtrer les candidatures du jour
        applications = Application.objects.filter(
            applied_at__date=today
        ).select_related(
            'candidate',
            'job',
            'job__company'
        )

        # Créer le fichier CSV en mémoire
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="candidatures_{today.strftime("%Y%m%d")}.csv"'

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
        for application in applications:
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

        # Enregistrer l'export dans la base de données
        csv_export = CSVExport.objects.create(
            export_type='APPLICATIONS',
            file_path=f"exports/candidatures_{today.strftime('%Y%m%d')}.csv",
            file_size=len(response.content),
            record_count=applications.count(),
            exported_by=request.user,
            filters_applied={
                'date': today.isoformat(),
                'export_type': 'daily_applications'
            }
        )

        return response

    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'export: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_applications_csv_custom(request):
    try:
        # Récupérer les paramètres de filtrage
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        status_filter = request.GET.get('status')
        company_id = request.GET.get('company_id')

        # Construire le queryset de base
        applications = Application.objects.select_related(
            'candidate',
            'job',
            'job__company'
        )

        # Appliquer les filtres
        if start_date:
            applications = applications.filter(applied_at__date__gte=start_date)
        if end_date:
            applications = applications.filter(applied_at__date__lte=end_date)
        if status_filter:
            applications = applications.filter(status=status_filter)
        if company_id:
            applications = applications.filter(job__company_id=company_id)

        # Si aucun filtre de date n'est spécifié, prendre les 30 derniers jours
        if not start_date and not end_date:
            thirty_days_ago = django_timezone.now().date() - django_timezone.timedelta(days=30)
            applications = applications.filter(applied_at__date__gte=thirty_days_ago)

        # Créer le fichier CSV
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        filename = f"candidatures_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

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
            'Téléphone du candidat',
            'Titre du poste',
            'Entreprise',
            'Type de contrat',
            'Niveau d\'expérience',
            'Localisation',
            'Télétravail',
            'Salaire min',
            'Salaire max',
            'Date d\'examen',
            'Examiné par',
            'Notes'
        ])

        # Écrire les données
        for application in applications:
            writer.writerow([
                application.id,
                application.applied_at.strftime('%d/%m/%Y %H:%M'),
                application.get_status_display(),
                application.candidate.get_full_name() or application.candidate.username,
                application.candidate.email,
                getattr(application.candidate.profile, 'phone', ''),
                application.job.title,
                application.job.company.name,
                application.job.get_contract_type_display(),
                application.job.get_experience_level_display(),
                application.job.location,
                'Oui' if application.job.is_remote else 'Non',
                application.job.salary_min or '',
                application.job.salary_max or '',
                application.reviewed_at.strftime('%d/%m/%Y %H:%M') if application.reviewed_at else '',
                application.reviewed_by.get_full_name() if application.reviewed_by else '',
                application.notes or ''
            ])

        # Enregistrer l'export dans la base de données
        csv_export = CSVExport.objects.create(
            export_type='APPLICATIONS',
            file_path=f"exports/{filename}",
            file_size=len(response.content),
            record_count=applications.count(),
            exported_by=request.user,
            filters_applied={
                'start_date': start_date,
                'end_date': end_date,
                'status': status_filter,
                'company_id': company_id,
                'export_type': 'custom_export'
            }
        )

        return response

    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'export: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
