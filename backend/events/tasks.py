from celery import shared_task
from RateOnline.storage_backends import PrivateMediaStorage
from users.utils import optimizing_with_current_size_image


@shared_task
def delete_photo_task(url_1, url_2):
    try:
        if url_1:
            PrivateMediaStorage().delete(url_1)
        if url_2:
            PrivateMediaStorage().delete(url_2)
    except Exception as e:
        print(e)


@shared_task
def optimize_photo(member_nomination_photo_id):
    from events.models import MemberNominationPhoto

    member_nom_photo = MemberNominationPhoto.objects.get(id=member_nomination_photo_id)
    source_image = PrivateMediaStorage().open(member_nom_photo.photo.name)

    file = optimizing_with_current_size_image(source_image)

    if not member_nom_photo.optimized_photo:
        member_nom_photo.optimized_photo = file
    else:
        member_nom_photo.optimized_photo.save(file.name, file, save=False)

    member_nom_photo._disable_signal = True
    member_nom_photo.save()
    del member_nom_photo._disable_signal
