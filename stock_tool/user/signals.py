from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, VirtualFunds

databases = ["mysql1", "mysql2", "mysql3"]


@receiver(post_save, sender=Profile)
def create_virtual_funds(sender, instance, created, **kwargs):
    if created:
        VirtualFunds.objects.using(databases[ord(instance.username[0]) % len(databases)]).create(user=instance, balance=50000.00)
