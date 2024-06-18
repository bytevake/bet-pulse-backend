from django.apps import AppConfig


class UseraccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'useraccounts'

    def ready(self):
        """
        Registering all signals in this app
        """
        from . import signals