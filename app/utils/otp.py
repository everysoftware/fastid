import random


def otp() -> str:
    return str(random.randint(100000, 999999))
