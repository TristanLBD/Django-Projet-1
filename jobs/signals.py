from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Application


@receiver(post_save, sender=Application)
def notify_employer_new_application(sender, instance, created, **kwargs):
    if created:
        # Récupérer l'employeur (créateur de l'annonce)
        employer = instance.job.created_by

        # Préparer les données pour l'email
        context = {
            'employer_name': employer.get_full_name() or employer.username,
            'candidate_name': instance.candidate.get_full_name() or instance.candidate.username,
            'job_title': instance.job.title,
            'company_name': instance.job.company.name,
            'application_date': instance.applied_at.strftime('%d/%m/%Y à %H:%M'),
            'application_url': f"{settings.SITE_URL}/admin/jobs/application/{instance.pk}/change/" if hasattr(settings, 'SITE_URL') else f"/admin/jobs/application/{instance.pk}/change/",
        }

        # Rendu du template email
        subject = f"Nouvelle candidature pour {instance.job.title}"
        html_message = render_to_string('jobs/email/new_application_notification.html', context)
        plain_message = render_to_string('jobs/email/new_application_notification.txt', context)

        # Envoi de l'email
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[employer.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            # En cas d'erreur d'envoi, on peut logger l'erreur
            print(f"Erreur lors de l'envoi de la notification: {e}")


@receiver(post_save, sender=Application)
def notify_candidate_application_status_change(sender, instance, **kwargs):
    if not kwargs.get('created', False):  # Seulement si ce n'est pas une nouvelle candidature
        # Récupérer l'ancienne instance pour comparer le statut
        try:
            old_instance = Application.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Le statut a changé, notifier le candidat
                context = {
                    'candidate_name': instance.candidate.get_full_name() or instance.candidate.username,
                    'job_title': instance.job.title,
                    'company_name': instance.job.company.name,
                    'old_status': old_instance.get_status_display(),
                    'new_status': instance.get_status_display(),
                    'status_change_date': instance.reviewed_at.strftime('%d/%m/%Y à %H:%M') if instance.reviewed_at else '',
                }

                subject = f"Mise à jour de votre candidature - {instance.job.title}"
                html_message = render_to_string('jobs/email/application_status_change.html', context)
                plain_message = render_to_string('jobs/email/application_status_change.txt', context)

                try:
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[instance.candidate.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Erreur lors de l'envoi de la notification de changement de statut: {e}")
        except Application.DoesNotExist:
            pass  # L'instance n'existe pas encore, c'est normal lors de la création
