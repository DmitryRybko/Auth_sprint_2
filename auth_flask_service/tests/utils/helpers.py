"""Helpers module."""

import random
import string


def get_random_string(char_num: int) -> str:
    """Return random string."""
    result: str = ''
    for x in range(random.randint(5, 10)):
        result += ''.join(random.choice(string.ascii_lowercase))
    return result


def get_random_email() -> str:
    """Return random email address."""
    random_email_name: str = get_random_string(random.randint(5, 10))
    random_email_domain: str = get_random_string(random.randint(5, 10))
    random_email_suffix: str = get_random_string(random.randint(2, 5))

    return f'{random_email_name}@{random_email_domain}.{random_email_suffix}'
