from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser
from .models import UserAccounts

@receiver(post_save, sender=CustomUser)
def create_user_account(sender, instance, created, **kwargs):
    """
    Used To Create An Account for Non Staff Users
    """
    if instance:
        if not instance.is_staff:
            # create a User Account
            user_account = UserAccounts(user_id=instance)
            user_account.save()