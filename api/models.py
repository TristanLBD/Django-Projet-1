from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CSVExport(models.Model):
    EXPORT_TYPES = [
        ('APPLICATIONS', 'Candidatures'),
        ('JOBS', 'Offres d\'emploi'),
        ('COMPANIES', 'Entreprises'),
    ]

    export_type = models.CharField(
        max_length=20,
        choices=EXPORT_TYPES,
        verbose_name="Type d'export"
    )
    file_path = models.CharField(
        max_length=500,
        verbose_name="Chemin du fichier"
    )
    file_size = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Taille du fichier (bytes)"
    )
    record_count = models.IntegerField(
        verbose_name="Nombre d'enregistrements"
    )
    exported_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Exporté par"
    )
    exported_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Exporté le"
    )
    filters_applied = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Filtres appliqués"
    )

    class Meta:
        verbose_name = "Export CSV"
        verbose_name_plural = "Exports CSV"
        ordering = ['-exported_at']

    def __str__(self):
        return f"Export {self.export_type} - {self.exported_at.strftime('%d/%m/%Y %H:%M')}"


class CSVImport(models.Model):
    IMPORT_TYPES = [
        ('APPLICATIONS', 'Candidatures'),
        ('JOBS', 'Offres d\'emploi'),
        ('COMPANIES', 'Entreprises'),
    ]

    import_type = models.CharField(
        max_length=20,
        choices=IMPORT_TYPES,
        verbose_name="Type d'import"
    )
    file_path = models.CharField(
        max_length=500,
        verbose_name="Chemin du fichier"
    )
    file_size = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Taille du fichier (bytes)"
    )
    records_processed = models.IntegerField(
        default=0,
        verbose_name="Enregistrements traités"
    )
    records_created = models.IntegerField(
        default=0,
        verbose_name="Enregistrements créés"
    )
    records_updated = models.IntegerField(
        default=0,
        verbose_name="Enregistrements mis à jour"
    )
    records_failed = models.IntegerField(
        default=0,
        verbose_name="Enregistrements échoués"
    )
    imported_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Importé par"
    )
    imported_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Importé le"
    )
    error_log = models.TextField(
        blank=True,
        verbose_name="Log d'erreurs"
    )

    class Meta:
        verbose_name = "Import CSV"
        verbose_name_plural = "Imports CSV"
        ordering = ['-imported_at']

    def __str__(self):
        return f"Import {self.import_type} - {self.imported_at.strftime('%d/%m/%Y %H:%M')}"
