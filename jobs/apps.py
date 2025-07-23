from django.apps import AppConfig


class JobsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobs'
    verbose_name = 'Offres d\'emploi et candidatures'

    def ready(self):
        """
        Import les signaux quand l'application est prête
        """
        import jobs.signals
