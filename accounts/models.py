from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('O', 'Autre'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Utilisateur"
    )
    photo = models.ImageField(
        upload_to='profiles/photos/',
        blank=True,
        null=True,
        verbose_name="Photo de profil"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone"
    )
    address = models.TextField(blank=True, verbose_name="Adresse")
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de naissance"
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        verbose_name="Genre"
    )
    bio = models.TextField(blank=True, verbose_name="Biographie")
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn")
    github_url = models.URLField(blank=True, verbose_name="GitHub")
    website_url = models.URLField(blank=True, verbose_name="Site web")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self):
        return f"Profil de {self.user.username}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('profile_detail', kwargs={'pk': self.pk})

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

    @property
    def application_count(self):
        return self.user.applications.count()

    @property
    def active_applications(self):
        return self.user.applications.filter(
            status__in=['PENDING', 'REVIEWED']
        )


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
