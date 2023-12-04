from django import forms as f
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_slug, URLValidator
from django.http import QueryDict

from api.db.config import SHORT_NAME_MIN_LENGTH, SHORT_NAME_MAX_LENGTH, FIRST_LAST_NAME_MIN_LENGTH, \
    FIRST_LAST_NAME_MAX_LENGTH, \
    PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH, URL_MAX_LENGTH, HEADER_MAX_LENGTH, MESSAGE_MAX_LENGTH, TEXT_MAX_LENGTH
from api.models import StudentGroup
from api.utils.strings_storage import StringStorage
from api.validators import validate_past_date, validate_beautiful_slug, validate_first_last_name


def update_form_data(form, data: dict):
    if not data:
        return form

    form_data = {}
    for key in dict(form.data).keys():
        form_data[key] = form.data[key]

    for key in data.keys():
        form_data[key] = data[key]

    form.data = QueryDict('&'.join([str(key) + '=' + str(form_data[key]) for key in form_data.keys()]))
    return form


class DateInput(f.DateInput):
    input_type = 'date'


class RegisterForm(f.Form):
    student_group = f.ModelChoiceField(queryset=StudentGroup.objects.all(),
                                       empty_label='- Группа не выбрана -',
                                       help_text=StringStorage.STUDENT_GROUP_HELP_TEXT.value,
                                       error_messages={'required': ''},
                                       widget=f.Select(attrs={
                                           'class': 'form-select'
                                       }),
                                       label='Группа')

    first_name = f.CharField(min_length=FIRST_LAST_NAME_MIN_LENGTH,
                             max_length=FIRST_LAST_NAME_MAX_LENGTH,
                             error_messages={'required': ''},
                             widget=f.TextInput(attrs={
                                 'class': 'form-input-text'
                             }),
                             validators=[validate_first_last_name],
                             label='Имя')

    last_name = f.CharField(min_length=FIRST_LAST_NAME_MIN_LENGTH,
                            max_length=FIRST_LAST_NAME_MAX_LENGTH,
                            error_messages={'required': ''},
                            widget=f.TextInput(attrs={
                                'class': 'form-input-text'
                            }),
                            validators=[validate_first_last_name],
                            label='Фамилия')

    username = f.CharField(min_length=SHORT_NAME_MIN_LENGTH,
                           max_length=SHORT_NAME_MAX_LENGTH,
                           help_text=StringStorage.USERNAME_HELP_TEXT.value,
                           error_messages={'required': ''},
                           widget=f.TextInput(attrs={
                               'class': 'form-input-text'
                           }),
                           validators=[validate_slug, validate_beautiful_slug],
                           label='Никнейм')

    birthday = f.DateField(error_messages={'required': ''},
                           widget=DateInput(attrs={
                               'class': 'form-select'
                           }),
                           validators=[validate_past_date],
                           label='Дата дня рождения')

    password = f.CharField(min_length=PASSWORD_MIN_LENGTH,
                           max_length=PASSWORD_MAX_LENGTH,
                           error_messages={'required': ''},
                           help_text=StringStorage.PASSWORD_HELP_TEXT.value,
                           widget=f.PasswordInput(attrs={
                               'class': 'form-input-text'
                           }),
                           validators=[validate_password],
                           label='Пароль')

    repeat_password = f.CharField(min_length=PASSWORD_MIN_LENGTH,
                                  max_length=PASSWORD_MAX_LENGTH,
                                  error_messages={'required': ''},
                                  widget=f.PasswordInput(attrs={
                                      'class': 'form-input-text'
                                  }),
                                  validators=[validate_password],
                                  label='Повторите пароль')


class LoginForm(f.Form):
    username = f.CharField(min_length=SHORT_NAME_MIN_LENGTH,
                           max_length=SHORT_NAME_MAX_LENGTH,
                           error_messages={'required': ''},
                           widget=f.TextInput(attrs={
                               'class': 'form-input-text',
                               'placeholder': 'Никнейм'
                           }),
                           validators=[validate_slug],
                           label='Никнейм')

    password = f.CharField(error_messages={'required': ''},
                           widget=f.PasswordInput(attrs={
                               'class': 'form-input-text',
                               'placeholder': 'Пароль'
                           }),
                           label='Пароль')


class UserEditForm(f.Form):
    username = f.CharField(min_length=SHORT_NAME_MIN_LENGTH,
                           max_length=SHORT_NAME_MAX_LENGTH,
                           help_text=StringStorage.USERNAME_HELP_TEXT.value,
                           error_messages={'required': ''},
                           widget=f.TextInput(attrs={
                               'class': 'form-input-text'
                           }),
                           required=False,
                           validators=[validate_slug],
                           label='Никнейм')

    image = f.FileField(error_messages={'required': ''},
                        required=False,
                        label='Аватарка')

    cover_image = f.FileField(error_messages={'required': ''},
                              required=False,
                              label='Обложка')

    birthday = f.DateField(error_messages={'required': ''},
                           widget=DateInput(attrs={
                               'class': 'form-select'
                           }),
                           required=False,
                           validators=[validate_past_date],
                           label='Дата дня рождения')

    about_me = f.CharField(max_length=SHORT_NAME_MAX_LENGTH,
                           help_text=StringStorage.ABOUT_ME_HELP_TEXT.value,
                           error_messages={'required': ''},
                           widget=f.TextInput(attrs={
                               'class': 'form-input-text form-max'
                           }),
                           required=False,
                           label='О себе')

    # telegram_username = f.CharField(max_length=URL_MAX_LENGTH,
    #                                 error_messages={'required': ''},
    #                                 help_text=StringStorage.TELEGRAM_NICKNAME.value,
    #                                 widget=f.TextInput(attrs={
    #                                     'class': 'form-input-text'
    #                                 }),
    #                                 required=False,
    #                                 validators=[validate_slug],
    #                                 label='Никнейм в Telegram')
    #
    # connect_telegram = f.BooleanField(error_messages={'required': ''},
    #                                   help_text=StringStorage.CONNECT_TELEGRAM.value,
    #                                   initial=False,
    #                                   widget=f.CheckboxInput(attrs={
    #                                       'class': 'form-checkbox'
    #                                   }),
    #                                   required=False,
    #                                   label='Подключить телеграм')

    # dark_theme = f.BooleanField(error_messages={'required': ''},
    #                             initial=False,
    #                             widget=f.CheckboxInput(attrs={
    #                                 'class': 'form-checkbox'
    #                             }),
    #                             required=False,
    #                             label='Темная тема')
    #
    # background_image = f.FileField(error_messages={'required': ''},
    #                                required=False,
    #                                label='Фоновое изображение')


class ProjectForm(f.Form):
    name = f.CharField(max_length=HEADER_MAX_LENGTH,
                       error_messages={'required': ''},
                       help_text=StringStorage.PROJECT_NAME_HELP_TEXT.value,
                       widget=f.TextInput(attrs={
                           'class': 'form-input-text form-long'
                       }),
                       required=False,
                       label='Тема проекта')

    document_url = f.CharField(max_length=URL_MAX_LENGTH,
                               error_messages={'required': ''},
                               help_text=StringStorage.DOCUMENT_URL.value,
                               widget=f.TextInput(attrs={
                                   'class': 'form-input-text form-long'
                               }),
                               required=False,
                               validators=[URLValidator],
                               label='Ссылка на Google-документ')

    figma_url = f.CharField(max_length=URL_MAX_LENGTH,
                            error_messages={'required': ''},
                            help_text=StringStorage.FIGMA_URL.value,
                            widget=f.TextInput(attrs={
                                'class': 'form-input-text form-long'
                            }),
                            required=False,
                            validators=[URLValidator],
                            label='Ссылка на дизайн в Figma')

    drawio_url = f.CharField(max_length=URL_MAX_LENGTH,
                             error_messages={'required': ''},
                             help_text=StringStorage.DRAWIO_URL.value,
                             widget=f.TextInput(attrs={
                                 'class': 'form-input-text form-long'
                             }),
                             required=False,
                             validators=[URLValidator],
                             label='Ссылка на диаграммы в Drawio')

    github_url = f.CharField(max_length=URL_MAX_LENGTH,
                             error_messages={'required': ''},
                             help_text=StringStorage.GITHUB_URL.value,
                             widget=f.TextInput(attrs={
                                 'class': 'form-input-text form-long'
                             }),
                             required=False,
                             validators=[URLValidator],
                             label='Ссылка на проект GitHub')


class HomeFilterForm(f.Form):
    student_group = f.ModelChoiceField(queryset=StudentGroup.objects.all(),
                                       empty_label='- Группа не выбрана -',
                                       error_messages={'required': ''},
                                       widget=f.Select(attrs={
                                           'class': 'form-select'
                                       }),
                                       required=False,
                                       label='Группа')

    only_current = f.BooleanField(error_messages={'required': ''},
                                  initial=False,
                                  widget=f.CheckboxInput(attrs={
                                      'class': 'form-checkbox'
                                  }),
                                  required=False,
                                  label='Показывать только актуальное')


class RatingFilterForm(f.Form):
    student_group = f.ModelChoiceField(queryset=StudentGroup.objects.all(),
                                       empty_label='- Группа не выбрана -',
                                       error_messages={'required': ''},
                                       widget=f.Select(attrs={
                                           'class': 'form-select'
                                       }),
                                       required=False,
                                       label='Группа')

    date_begin = f.DateField(error_messages={'required': ''},
                             widget=DateInput(attrs={
                                 'class': 'form-select form-short'
                             }),
                             required=False,
                             label='С')

    date_end = f.DateField(error_messages={'required': ''},
                           widget=DateInput(attrs={
                               'class': 'form-select form-short'
                           }),
                           required=False,
                           label='до')

    sort_by_points_change = f.BooleanField(error_messages={'required': ''},
                                           initial=False,
                                           widget=f.CheckboxInput(attrs={
                                               'class': 'form-checkbox'
                                           }),
                                           required=False,
                                           label='Сортировка по изменению баллов')


class FeedbackForm(f.Form):
    text = f.CharField(max_length=MESSAGE_MAX_LENGTH,
                       help_text=f'Здесь вы можете оставить любое сообщение для вашего преподавателя: '
                                 f'что нравится, что не нравится, что можно улучшить и т.д. '
                                 f'Сообщение анонимное — отправитель останется в тени',
                       error_messages={'required': ''},
                       widget=f.Textarea(attrs={
                           'class': 'form-input-text form-max',
                           'rows': 6,
                       }),
                       label='Расскажите о том, как вам занятия')


class CommentForm(f.Form):
    text = f.CharField(max_length=TEXT_MAX_LENGTH,
                       error_messages={'required': ''},
                       widget=f.Textarea(attrs={
                           'class': 'form-input-text form-max',
                           'rows': 4,
                       }),
                       required=False,
                       label='Текст')
