import random
import string

DEFAULT_CHAR_STRING = string.ascii_lowercase + string.digits


def generate_random_string(char=DEFAULT_CHAR_STRING, size=6):
    return ''.join(random.choice(char) for _ in range(size))
