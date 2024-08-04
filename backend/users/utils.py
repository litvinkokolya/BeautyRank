import random


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

