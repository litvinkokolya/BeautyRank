import random
from io import BytesIO
from os.path import basename, splitext
from django.core.files import File
from PIL import Image, ImageOps


def generate_password() -> str:
    pair = str(random.randint(0, 9)) * 2
    remaining_digits = [str(random.randint(0, 9)) for _ in range(2)]
    random.shuffle(remaining_digits)

    position = random.choice(["start", "middle", "end"])
    if position == "start":
        password = pair + "".join(remaining_digits)
    elif position == "middle":
        password = remaining_digits[0] + pair + remaining_digits[1]
    else:
        password = "".join(remaining_digits) + pair

    return password


def optimizing_with_current_size_image(source_image, max_size=100):
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
