from os.path import basename

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from RateOnline.storage_backends import PrivateMediaStorage
from events.tasks import optimize_image
from users.models import User


@receiver(post_save, sender=User)
def make_image_optimized(sender, instance, **kwargs):
    if hasattr(instance, "_disable_signal"):
        return

    try:
        is_have_image = bool(instance.image)
        is_have_optimized_image = bool(instance.optimized_image)
        equal_images = False

        if is_have_image and is_have_optimized_image:
            equal_images = basename(instance.image.name) == basename(
                instance.optimized_image.name
            )

        if is_have_image and (not is_have_optimized_image or equal_images is False):
            optimized_image = optimize_image.delay(instance.image, 150)
            if not instance.optimized_image:
                instance.optimized_image = optimized_image
            else:
                instance.optimized_image.save(
                    optimized_image.name, optimized_image, save=False
                )

            instance._disable_signal = True
            instance.save()
            del instance._disable_signal

    except Exception as e:
        print(f"Ошибка во время оптимизации фото: {e}")


@receiver(post_delete, sender=User)
def delete_objects_user(sender, instance, **kwargs):
    if instance.image:
        PrivateMediaStorage().delete(instance.image.name)
    if instance.optimized_image:
        PrivateMediaStorage().delete(instance.optimized_image.name)
