from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """
    Inline pour afficher le profil utilisateur dans l'admin User
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = [
        'photo',
        'phone',
        'address',
        'birth_date',
        'gender',
        'bio',
        'linkedin_url',
        'github_url',
        'website_url'
    ]


class UserAdmin(BaseUserAdmin):
    """
    Interface d'administration personnalisée pour les utilisateurs
    """
    inlines = (UserProfileInline,)
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_superuser',
        'application_count',
        'date_joined'
    ]
    list_filter = [
        'is_staff',
        'is_superuser',
        'is_active',
        'date_joined',
        'profile__gender'
    ]
    search_fields = [
        'username',
        'first_name',
        'last_name',
        'email',
        'profile__phone'
    ]

    def application_count(self, obj):
        """Affiche le nombre de candidatures de l'utilisateur"""
        count = obj.applications.count()
        if count > 0:
            from django.urls import reverse
            url = reverse('admin:jobs_application_changelist') + f'?candidate__id__exact={obj.id}'
            return format_html('<a href="{}">{} candidature(s)</a>', url, count)
        return "0 candidature"
    application_count.short_description = "Candidatures"


# Réenregistrer l'admin User avec notre version personnalisée
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les profils utilisateurs
    """
    list_display = [
        'user',
        'full_name',
        'phone',
        'gender',
        'photo_preview',
        'application_count',
        'created_at'
    ]
    list_filter = ['gender', 'created_at', 'updated_at']
    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        'phone'
    ]
    readonly_fields = ['created_at', 'updated_at', 'photo_preview', 'application_count']

    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Informations personnelles', {
            'fields': ('photo', 'photo_preview', 'phone', 'address', 'birth_date', 'gender')
        }),
        ('Biographie', {
            'fields': ('bio',)
        }),
        ('Réseaux sociaux', {
            'fields': ('linkedin_url', 'github_url', 'website_url'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def full_name(self, obj):
        """Affiche le nom complet de l'utilisateur"""
        return obj.full_name
    full_name.short_description = "Nom complet"
    full_name.admin_order_field = 'user__first_name'

    def photo_preview(self, obj):
        """Affiche un aperçu de la photo de profil"""
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.photo.url
            )
        return "Aucune photo"
    photo_preview.short_description = "Photo de profil"

    def application_count(self, obj):
        """Affiche le nombre de candidatures"""
        return obj.application_count
    application_count.short_description = "Nombre de candidatures"
