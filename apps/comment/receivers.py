from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from common.index import save_record

from .models import Comment


@receiver(post_save, sender=Comment)
@receiver(post_delete, sender=Comment)
def save_commented_object_record_index(sender, instance, **kwargs):
    # Update record index
    save_record(instance=instance.commented_object, update_fields=('comments_count',))
