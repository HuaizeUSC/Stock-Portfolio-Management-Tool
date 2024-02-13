from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, VirtualFunds


@receiver(post_save, sender=Profile)
def create_virtual_funds(sender, instance, created, **kwargs):
    if created:
        VirtualFunds.objects.create(user=instance, balance=0)
