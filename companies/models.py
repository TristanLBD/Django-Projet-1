from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Company(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    description = models.TextField(verbose_name="Description")
    address = models.TextField(verbose_name="Adresse")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Email")
    website = models.URLField(blank=True, null=True, verbose_name="Site web")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Créé par",
        related_name='companies_created'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('company_detail', kwargs={'pk': self.pk})


class CompanyPhoto(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name="Entreprise"
    )
    image = models.ImageField(
        upload_to='companies/photos/',
        verbose_name="Photo"
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Légende"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploadé le")
    is_primary = models.BooleanField(default=False, verbose_name="Photo principale")

    class Meta:
        verbose_name = "Photo d'entreprise"
        verbose_name_plural = "Photos d'entreprise"
        ordering = ['-is_primary', '-uploaded_at']

    def __str__(self):
        return f"Photo de {self.company.name} - {self.caption or 'Sans légende'}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            CompanyPhoto.objects.filter(
                company=self.company,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
