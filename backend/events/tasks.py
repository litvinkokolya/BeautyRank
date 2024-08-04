from celery import shared_task
from io import BytesIO
from os.path import basename, splitext
from django.core.files import File
from PIL import Image, ImageOps
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


@shared_task
def optimize_image(source_image, max_size):
    img = Image.open(source_image)

    img = ImageOps.exif_transpose(img)

    original_width, original_height = img.size
    if original_width > original_height:
        new_width = max_size
        new_height = int((max_size / original_width) * original_height)
    else:
        new_height = max_size
        new_width = int((max_size / original_height) * original_width)

    img = img.resize((new_width, new_height))

    buffer = BytesIO()
    img.save(buffer, format="webp", quality=80, lossless=True)

    buffer.seek(0)

    return File(buffer, name=splitext(basename(source_image.name))[0] + ".webp")
