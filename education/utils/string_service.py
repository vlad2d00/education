import re


def get_cropped_text(text: str, max_size):
    text = text.strip()
    if len(text) <= max_size:
        return text

    i = max_size - 1
    while i >= 0 and text[i] <= ' ':
        i -= 1

    return text[:i + 1] + '...'


def is_name(value: str) -> bool:
    if not value:
        return False

    if 'a' <= value[0] <= 'z' or 'A' <= value[0] <= 'Z':
        if re.fullmatch(r'[A-Za-z][A-Za-z-]*[A-Za-z]', value) is None:
            return False
    else:
        if re.fullmatch(r'[А-Яа-я][А-Яа-я-]*[А-Яа-я]', value) is None:
            return False

    i = 1
    while i < len(value):
        if value[i] in '-' and i > 0 and value[i - 1] in '-':
            return False
        i += 1
    return True


def is_full_name(value: str) -> bool:
    values = value.split()
    if not values:
        return False

    for value in values:
        if not is_name(value):
            return False

    return True


def is_beautiful_slug(value: str) -> bool:
    if not value or value[0].isdigit():
        return False

    i = 1
    while i < len(value):
        if value[i] in '_' and i > 0 and value[i - 1] in '_':
            return False
        i += 1
    return True
