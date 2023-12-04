from django.core.exceptions import ValidationError

from education.utils.string_service import is_full_name, is_beautiful_slug, is_name
from education.utils.datetime_service import datetime_now


def validate_past_date(value):
    if value > datetime_now().date():
        raise ValidationError(
            message='Недопустимо выбирать дату из будущего',
        )


def validate_first_last_name(value: str):
    if not is_name(value):
        raise ValidationError(
            message='Строка не подходит под формат имени / фамилии',
        )


def validate_full_name(value: str):
    if not is_full_name(value):
        raise ValidationError(
            message='Строка не подходит под формат полного имени',
        )


def validate_beautiful_slug(value: str):
    if not is_beautiful_slug(value):
        raise ValidationError(
            message='Значение не должно начинаться с цифры, а так же начинаться, заканчиваться или '
                    'иметь два подряд идущих символа \'_\'',
        )


def validate_figma_url(value: str):
    if 'figma.com' not in value:
        raise ValidationError(
            message='Ссылка не является ссылкой на Figma проект',
        )


def validate_drawio_url(value: str):
    if 'diagrams.net' not in value:
        raise ValidationError(
            message='Ссылка не является ссылкой на Drawio проект',
        )


def validate_github_url(value: str):
    if 'github.com' not in value:
        raise ValidationError(
            message='Ссылка не является ссылкой на GitHub проект',
        )


def validate_document_url(value: str):
    if 'docs.google.com' not in value:
        raise ValidationError(
            message='Ссылка не является ссылкой на Google Document',
        )
