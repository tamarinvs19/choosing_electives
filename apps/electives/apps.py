from django.apps import AppConfig


class ElectivesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.electives'

    def ready(self):
        import apps.electives.signals
