from celery import shared_task

from RateOnline.storage_backends import PrivateMediaStorage


@shared_task
def delete_photo_task(url_1, url_2):
    try:
        if url_1:
            PrivateMediaStorage().delete(url_1)
        if url_2:
            PrivateMediaStorage().delete(url_2)
    except Exception as e:
        print(e)
