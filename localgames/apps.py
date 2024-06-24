from django.apps import AppConfig


class LocalgamesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'localgames'

    def ready(self):
        """
        Registering all signals in this app
        """
        from . import signals