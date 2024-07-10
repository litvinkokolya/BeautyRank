from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from events.models import MemberNomination, MemberNominationPhoto, Result
from integrations.telegram import TelegramIntegration
from events.tasks import delete_photo_task


@receiver(post_save, sender=MemberNomination)
def save_url(sender, instance, **kwargs):
    if instance.url_video and not instance.url_message_video:
        integration = TelegramIntegration()
        integration.send_video_to_telegram_channel(instance)


@receiver(post_delete, sender=MemberNominationPhoto)
def delete_objects_of_member_nomination_photo(sender, instance, **kwargs):
    delete_photo_task.delay(instance.photo.name, instance.optimized_photo.name)


@receiver(post_save, sender=Result)
def save_member_nominations(sender, instance, **kwargs):
    instance.member_nomination.save()
