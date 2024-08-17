from os.path import basename

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from events.models import MemberNomination, MemberNominationPhoto, Result
from integrations.telegram import TelegramIntegration
from events.tasks import delete_photo_task, optimize_photo


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


@receiver(post_save, sender=MemberNominationPhoto)
def make_photo_optimized(sender, instance, **kwargs):
    if hasattr(instance, "_disable_signal"):
        return

    try:
        is_have_photo = bool(instance.photo)
        is_have_optimized_photo = bool(instance.optimized_photo)
        equal_photos = False

        if is_have_photo and is_have_optimized_photo:
            equal_photos = basename(instance.photo.name) == basename(
                instance.optimized_photo.name
            )

        if is_have_photo and equal_photos is False:
            optimize_photo.delay(instance.id)

    except Exception as e:
        print(f"Ошибка во время оптимизации фото: {e}")
