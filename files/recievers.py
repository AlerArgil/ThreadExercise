import threading

from django.db.models.signals import post_save
from django.dispatch import receiver

from files.models import CSV


@receiver(post_save, sender=CSV)
def parse_file(sender, instance, created, **kwargs):
    """
    Start Thread with parsing function for new file
    """

    if created:
        thread = threading.Thread(target=instance.parsing, args=[])
        thread.start()


