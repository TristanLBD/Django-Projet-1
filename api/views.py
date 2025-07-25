import csv
import io
from datetime import datetime
from django.http import HttpResponse
from django.utils import timezone
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from jobs.models import Application, Job
from companies.models import Company


class ExportApplicationsTodayCSVView(View):
    """Vue API pour exporter les candidatures du jour en CSV"""

    def get(self, request):
        try:
            # Récupérer la date d'aujourd'hui
            today = timezone.now().date()

            # Filtrer les candidatures du jour
            applications = Application.objects.filter(
                applied_at__date=today
            ).select_related(
                'candidate',
                'job',
                'job__company',
                'reviewed_by'
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

            return response

        except Exception as e:
            return HttpResponse(
                f'Erreur lors de l\'export: {str(e)}',
                status=500,
                content_type='text/plain'
            )


class ExportAllApplicationsCSVView(View):
    """Vue API pour exporter toutes les candidatures en CSV"""

    def get(self, request):
        try:
            # Récupérer toutes les candidatures
            applications = Application.objects.all().select_related(
                'candidate',
                'job',
                'job__company',
                'reviewed_by'
            )

            # Créer le fichier CSV en mémoire
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="candidatures_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'

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

            return response

        except Exception as e:
            return HttpResponse(
                f'Erreur lors de l\'export: {str(e)}',
                status=500,
                content_type='text/plain'
            )


class ImportApplicationsCSVView(View):
    """Vue API pour importer des candidatures depuis un fichier CSV"""

    def get(self, request):
        """Afficher le formulaire d'import"""
        return render(request, 'admin/jobs/application/import_form.html', {
            'title': 'Importer des candidatures depuis un fichier CSV',
            'opts': {'app_label': 'jobs', 'model_name': 'application'},
        })

    def post(self, request):
        """Traiter l'import du fichier CSV"""
        if not request.FILES.get('csv_file'):
            messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('admin:jobs_application_changelist')

        csv_file = request.FILES['csv_file']

        # Vérifier l'extension du fichier
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Le fichier doit être au format CSV.')
            return redirect('admin:jobs_application_changelist')

        try:
            # Lire le fichier CSV
            decoded_file = csv_file.read().decode('utf-8-sig')  # Gérer le BOM
            csv_data = csv.reader(io.StringIO(decoded_file), delimiter=';')

            # Ignorer l'en-tête
            next(csv_data, None)

            records_processed = 0
            records_created = 0
            records_updated = 0
            records_failed = 0
            error_log = []

            for row in csv_data:
                if len(row) < 6:  # Vérifier qu'il y a assez de colonnes
                    records_failed += 1
                    error_log.append(f"Ligne {records_processed + 1}: Nombre de colonnes insuffisant")
                    continue

                try:
                    # Extraire les données de la ligne
                    candidate_email = row[4].strip()  # Email du candidat
                    job_title = row[5].strip()  # Titre du poste
                    company_name = row[6].strip()  # Nom de l'entreprise
                    status = row[2].strip()  # Statut

                    # Trouver ou créer l'utilisateur
                    user, created = User.objects.get_or_create(
                        email=candidate_email,
                        defaults={
                            'username': candidate_email.split('@')[0],
                            'first_name': row[3].split()[0] if row[3] else '',
                            'last_name': ' '.join(row[3].split()[1:]) if row[3] and len(row[3].split()) > 1 else '',
                        }
                    )

                    # Trouver ou créer l'entreprise
                    company, created = Company.objects.get_or_create(
                        name=company_name,
                        defaults={
                            'description': f'Entreprise importée depuis CSV',
                            'is_active': True,
                            'created_by': request.user
                        }
                    )

                    # Trouver ou créer l'offre d'emploi
                    job, created = Job.objects.get_or_create(
                        title=job_title,
                        company=company,
                        defaults={
                            'description': f'Offre importée depuis CSV',
                            'contract_type': 'CDI',
                            'location': 'Non spécifié',
                            'is_active': True,
                            'created_by': request.user
                        }
                    )

                    # Créer la candidature
                    application, created = Application.objects.get_or_create(
                        candidate=user,
                        job=job,
                        defaults={
                            'status': 'PENDING',
                            'cover_letter': f'Candidature importée depuis CSV le {datetime.now().strftime("%d/%m/%Y")}'
                        }
                    )

                    if created:
                        records_created += 1
                    else:
                        records_updated += 1

                    records_processed += 1

                except Exception as e:
                    records_failed += 1
                    error_log.append(f"Ligne {records_processed + 1}: {str(e)}")
                    continue

            # Afficher les messages de succès/erreur
            if records_created > 0:
                messages.success(request, f'{records_created} candidature(s) créée(s) avec succès.')
            if records_updated > 0:
                messages.info(request, f'{records_updated} candidature(s) mise(s) à jour.')
            if records_failed > 0:
                messages.warning(request, f'{records_failed} candidature(s) n\'ont pas pu être importées.')

            return redirect('admin:jobs_application_changelist')

        except Exception as e:
            messages.error(request, f'Erreur lors de l\'import: {str(e)}')
            return redirect('admin:jobs_application_changelist')
