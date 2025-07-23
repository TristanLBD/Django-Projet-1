from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from companies.models import Company


class Job(models.Model):
    CONTRACT_TYPES = [
        ('CDI', 'Contrat à durée indéterminée'),
        ('CDD', 'Contrat à durée déterminée'),
        ('STAGE', 'Stage'),
        ('ALTERNANCE', 'Alternance'),
        ('FREELANCE', 'Freelance'),
        ('INTERIM', 'Intérim'),
    ]

    EXPERIENCE_LEVELS = [
        ('DEBUTANT', 'Débutant'),
        ('JUNIOR', 'Junior (1-3 ans)'),
        ('SENIOR', 'Senior (3-5 ans)'),
        ('EXPERT', 'Expert (5+ ans)'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre du poste")
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='jobs',
        verbose_name="Entreprise"
    )
    description = models.TextField(verbose_name="Description du poste")
    requirements = models.TextField(verbose_name="Prérequis")
    contract_type = models.CharField(
        max_length=20,
        choices=CONTRACT_TYPES,
        verbose_name="Type de contrat"
    )
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_LEVELS,
        verbose_name="Niveau d'expérience"
    )
    salary_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Salaire minimum"
    )
    salary_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Salaire maximum"
    )
    location = models.CharField(max_length=200, verbose_name="Localisation")
    is_remote = models.BooleanField(default=False, verbose_name="Télétravail possible")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Créé par",
        related_name='jobs_created'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    is_filled = models.BooleanField(default=False, verbose_name="Poste pourvu")

    class Meta:
        verbose_name = "Offre d'emploi"
        verbose_name_plural = "Offres d'emploi"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.company.name}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('job_detail', kwargs={'pk': self.pk})

    @property
    def is_available(self):
        return self.is_active and not self.is_filled

    @property
    def application_count(self):
        return self.applications.count()


class Application(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('REVIEWED', 'En cours d\'examen'),
        ('ACCEPTED', 'Acceptée'),
        ('REJECTED', 'Refusée'),
        ('WITHDRAWN', 'Retirée'),
    ]

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name="Offre d'emploi"
    )
    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name="Candidat"
    )
    cover_letter = models.TextField(verbose_name="Lettre de motivation")
    resume = models.FileField(
        upload_to='applications/resumes/',
        verbose_name="CV"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Statut"
    )
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name="Candidature déposée le")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Examinée le")
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications_reviewed',
        verbose_name="Examinée par"
    )
    notes = models.TextField(blank=True, verbose_name="Notes")

    class Meta:
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"
        ordering = ['-applied_at']
        unique_together = ['job', 'candidate']  # Un candidat ne peut postuler qu'une fois par poste

    def __str__(self):
        return f"Candidature de {self.candidate.username} pour {self.job.title}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('application_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = Application.objects.get(pk=self.pk)
            if old_instance.status != self.status:
                self.reviewed_at = timezone.now()
        super().save(*args, **kwargs)
