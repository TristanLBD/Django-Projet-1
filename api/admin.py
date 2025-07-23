from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import CSVExport, CSVImport


@admin.register(CSVExport)
class CSVExportAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les exports CSV
    """
    list_display = [
        'export_type',
        'record_count',
        'exported_by',
        'exported_at',
        'file_size_display'
    ]
    list_filter = ['export_type', 'exported_at', 'exported_by']
    search_fields = ['exported_by__username', 'exported_by__email']
    readonly_fields = [
        'export_type',
        'file_path',
        'file_size',
        'record_count',
        'exported_by',
        'exported_at',
        'filters_applied_display'
    ]

    fieldsets = (
        ('Informations de l\'export', {
            'fields': ('export_type', 'record_count', 'exported_by', 'exported_at')
        }),
        ('Fichier', {
            'fields': ('file_path', 'file_size_display')
        }),
        ('Filtres appliqués', {
            'fields': ('filters_applied_display',),
            'classes': ('collapse',)
        }),
    )

    def file_size_display(self, obj):
        """Affiche la taille du fichier de manière lisible"""
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} B"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "N/A"
    file_size_display.short_description = "Taille du fichier"

    def filters_applied_display(self, obj):
        """Affiche les filtres appliqués de manière lisible"""
        if obj.filters_applied:
            filters_text = []
            for key, value in obj.filters_applied.items():
                if value:
                    filters_text.append(f"{key}: {value}")
            return ", ".join(filters_text) if filters_text else "Aucun filtre"
        return "Aucun filtre"
    filters_applied_display.short_description = "Filtres appliqués"

    def has_add_permission(self, request):
        """Empêche l'ajout manuel d'exports"""
        return False

    def has_change_permission(self, request, obj=None):
        """Empêche la modification des exports"""
        return False


@admin.register(CSVImport)
class CSVImportAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les imports CSV
    """
    list_display = [
        'import_type',
        'records_processed',
        'records_created',
        'records_updated',
        'records_failed',
        'imported_by',
        'imported_at',
        'file_size_display'
    ]
    list_filter = ['import_type', 'imported_at', 'imported_by']
    search_fields = ['imported_by__username', 'imported_by__email']
    readonly_fields = [
        'import_type',
        'file_path',
        'file_size',
        'records_processed',
        'records_created',
        'records_updated',
        'records_failed',
        'imported_by',
        'imported_at',
        'error_log_display'
    ]

    fieldsets = (
        ('Informations de l\'import', {
            'fields': ('import_type', 'imported_by', 'imported_at')
        }),
        ('Fichier', {
            'fields': ('file_path', 'file_size_display')
        }),
        ('Résultats', {
            'fields': ('records_processed', 'records_created', 'records_updated', 'records_failed')
        }),
        ('Log d\'erreurs', {
            'fields': ('error_log_display',),
            'classes': ('collapse',)
        }),
    )

    def file_size_display(self, obj):
        """Affiche la taille du fichier de manière lisible"""
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} B"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "N/A"
    file_size_display.short_description = "Taille du fichier"

    def error_log_display(self, obj):
        """Affiche le log d'erreurs de manière formatée"""
        if obj.error_log:
            return format_html('<pre style="max-height: 200px; overflow-y: auto;">{}</pre>', obj.error_log)
        return "Aucune erreur"
    error_log_display.short_description = "Log d'erreurs"

    def has_add_permission(self, request):
        """Empêche l'ajout manuel d'imports"""
        return False

    def has_change_permission(self, request, obj=None):
        """Empêche la modification des imports"""
        return False
