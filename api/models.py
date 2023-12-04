from django.contrib.auth.models import User
from django.core.validators import URLValidator, MinValueValidator
from django.db import models as m
from django.urls import reverse

from api.db.config import *
from education.utils.string_service import get_cropped_text
from api.validators import validate_past_date, validate_figma_url, validate_github_url, validate_drawio_url, \
    validate_document_url
from education.utils.datetime_service import datetime_to_string, datetime_timezone


class System(m.Model):
    version = m.CharField(max_length=VERSION_MAX_LENGTH, default='1.0.0', verbose_name='Версия')
    hide_rating = m.BooleanField(default=False, verbose_name='Скрыть рейтинг')

    def __str__(self):
        return self.version

    class Meta:
        verbose_name = 'Система'
        verbose_name_plural = 'Система'


class TechnicalWork(m.Model):
    datetime_begin = m.DateTimeField(verbose_name='Дата и время начала')
    datetime_end = m.DateTimeField(verbose_name='Дата и время завершения')
    description = m.CharField(max_length=MESSAGE_MAX_LENGTH, verbose_name='Описание')

    def __str__(self):
        return datetime_to_string(datetime_timezone(self.datetime_begin)) + ' - ' + \
               datetime_to_string(datetime_timezone(self.datetime_end))

    class Meta:
        verbose_name = 'Технические работы на сервере'
        verbose_name_plural = 'Технические работы на сервере'
        ordering = ['-datetime_begin']


class LinkGroup(m.Model):
    name = m.CharField(max_length=HEADER_MAX_LENGTH, unique=True, verbose_name='Название')
    position = m.PositiveIntegerField(default=0, verbose_name='Позиция в списке')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Группа ссылок'
        verbose_name_plural = 'Группы ссылок'
        ordering = ['position']


class Link(m.Model):
    datetime_create = m.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    name = m.CharField(max_length=HEADER_MAX_LENGTH, unique=True, verbose_name='Название')
    description = m.TextField(max_length=MESSAGE_MAX_LENGTH, null=True, blank=True, verbose_name='Описание')
    url = m.CharField(max_length=URL_MAX_LENGTH, unique=True, verbose_name='Ссылка',
                      validators=(URLValidator(),))
    position = m.PositiveIntegerField(default=0, verbose_name='Позиция в списке')

    group = m.ForeignKey(LinkGroup, on_delete=m.CASCADE, verbose_name='Группа')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('links')

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'
        ordering = ['position']


class Mark(m.Model):
    name = m.CharField(max_length=NAME_MAX_LENGTH, unique=True, verbose_name='Название')
    value = m.PositiveIntegerField(unique=True, verbose_name='Значение')
    complete_percent = m.PositiveIntegerField(unique=True, verbose_name='Процент выполнения')

    def __str__(self):
        return str(self.value) + ' (' + str(self.complete_percent) + '%) - ' + self.name

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        ordering = ['-name']


class TestPenaltyDelay(m.Model):
    seconds = m.PositiveIntegerField(verbose_name='Количество секунд')
    points_loss_percent = m.PositiveIntegerField(verbose_name='Снятие процентов баллов')

    def __str__(self):
        return str(self.points_loss_percent) + '% per ' + str(self.seconds) + ' seconds'

    class Meta:
        verbose_name = 'Штраф за задержку выполнения тестирования'
        verbose_name_plural = 'Штраф за задержку выполнения тестирования'


class BlockedUser(m.Model):
    datetime_unlock = m.DateTimeField(null=True, blank=True, verbose_name='Дата и время разблокировки')
    cause = m.TextField(max_length=MESSAGE_MAX_LENGTH, null=True, blank=True, verbose_name='Причина')

    user = m.OneToOneField(User, on_delete=m.CASCADE, db_index=True, verbose_name='Пользователь')

    def __str__(self):
        return str(self.user) + ' - ' + datetime_to_string(datetime_timezone(self.datetime_unlock))

    def get_absolute_url(self):
        return reverse('user', args=(self.user.id,))

    class Meta:
        verbose_name = 'Блокировка пользователя'
        verbose_name_plural = 'Заблокированные пользователи'
        ordering = ['-datetime_unlock']


class NoticeType(m.Model):
    name = m.TextField(max_length=HEADER_MAX_LENGTH, verbose_name='Название')
    code = m.PositiveIntegerField(unique=True, db_index=True, editable=False, verbose_name='Код')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип уведомления'
        verbose_name_plural = 'Типы уведомлений'
        ordering = ['code']


class Notice(m.Model):
    datetime_create = m.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    kwargs = m.JSONField(max_length=ARGS_MAX_LENGTH, null=True, blank=True, verbose_name='Словарь аргументов')
    is_read = m.BooleanField(default=False, verbose_name='Прочитано')

    user = m.ForeignKey(User, on_delete=m.CASCADE, db_index=True, verbose_name='Пользователь')
    notice_type = m.ForeignKey(NoticeType, on_delete=m.CASCADE, db_index=True, verbose_name='Тип')

    def __str__(self):
        return str(self.user) + ' - ' + str(self.notice_type)

    def get_absolute_url(self):
        return reverse('notices')

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-datetime_create']


class IPAddress(m.Model):
    value = m.CharField(max_length=IP_ADDRESS_MAX_LENGTH, unique=True, db_index=True, verbose_name='Значение')
    last_minute_requests = m.PositiveIntegerField(default=0, verbose_name='Запросов за последнюю минуту')

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = 'IP адрес'
        verbose_name_plural = 'IP адреса'


class BlockedIPAddress(m.Model):
    datetime_unlock = m.DateTimeField(null=True, blank=True, verbose_name='Дата и время разблокировки')
    cause = m.TextField(max_length=MESSAGE_MAX_LENGTH, null=True, blank=True, verbose_name='Причина')

    ip_address = m.OneToOneField(IPAddress, on_delete=m.CASCADE, unique=True, db_index=True, verbose_name='IP адрес')

    def __str__(self):
        return str(self.ip_address) + ' - ' + datetime_to_string(datetime_timezone(self.datetime_unlock))

    class Meta:
        verbose_name = 'Блокировка по IP адрес'
        verbose_name_plural = 'Заблокированные IP адреса'
        ordering = ['-datetime_unlock']


class UserAgent(m.Model):
    value = m.CharField(max_length=USER_AGENT_MAX_LENGTH, unique=True, verbose_name='Значение')

    def __str__(self):
        return get_cropped_text(self.value, max_size=ADMIN_CROPPED_TEXT_SIZE)

    class Meta:
        verbose_name = 'User agent'
        verbose_name_plural = 'User agents'


class RequestMethod(m.Model):
    name = m.CharField(max_length=NAME_MAX_LENGTH, unique=True, db_index=True, verbose_name='Имя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Метод запроса'
        verbose_name_plural = 'Методы запроса'


class Log(m.Model):
    datetime_create = m.DateTimeField(auto_now_add=True, verbose_name='Дата и время')
    path = m.CharField(max_length=PATH_MAX_LENGTH, verbose_name='Путь')
    kwargs = m.JSONField(max_length=ARGS_MAX_LENGTH, null=True, blank=True, verbose_name='Словарь аргументов')
    status_code = m.PositiveIntegerField(verbose_name='Код ответа')

    method = m.ForeignKey(RequestMethod, on_delete=m.CASCADE, verbose_name='Метод запроса')
    user = m.ForeignKey(User, on_delete=m.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    ip_address = m.ForeignKey(IPAddress, on_delete=m.SET_NULL, null=True, blank=True, verbose_name='IP адрес')
    user_agent = m.ForeignKey(UserAgent, on_delete=m.SET_NULL, null=True, blank=True, verbose_name='User agent')

    def __str__(self):
        return ('[' + datetime_to_string(datetime_timezone(self.datetime_create)) + ']' +
                ' ' + str(self.path) +
                ' ' + str(self.method) +
                ' ' + str(self.status_code) +
                (f' params={self.kwargs}' if self.kwargs else '') +
                (f' username=\"{self.user.username}\"' if self.user else '') +
                (f' ip_address=\"{self.ip_address}\"' if self.ip_address else ''))

    class Meta:
        verbose_name = 'Запись в журнале'
        verbose_name_plural = 'Записи в журнале'
        ordering = ['-datetime_create']


class UserActionType(m.Model):
    name = m.CharField(max_length=HEADER_MAX_LENGTH, null=True, blank=True, verbose_name='Название')
    code = m.PositiveIntegerField(unique=True, db_index=True, editable=False, verbose_name='Код')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип действия пользователя'
        verbose_name_plural = 'Типы действий пользователей'
        ordering = ['code']


class UserAction(m.Model):
    datetime_create = m.DateTimeField(auto_now_add=True, verbose_name='Дата и время')
    kwargs = m.JSONField(max_length=ARGS_MAX_LENGTH, null=True, blank=True, verbose_name='Словарь аргументов')

    user = m.ForeignKey(User, on_delete=m.CASCADE, verbose_name='Пользователь')
    action_type = m.ForeignKey(UserActionType, on_delete=m.CASCADE, verbose_name='Тип действия')

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Действие пользователя'
        verbose_name_plural = 'Действия пользователей'
        ordering = ['action_type__code']


class UserActivity(m.Model):
    datetime_last_activity = m.DateTimeField(verbose_name='Дата и время последнего действия')
    online_days_in_a_row = m.PositiveIntegerField(default=1, verbose_name='Онлайн дней подряд')
    online_days_in_a_row_max = m.PositiveIntegerField(default=1, verbose_name='Онлайн дней подряд максимум')
    date_last_online = m.DateField(verbose_name='Дата последнего онлайна')

    user = m.OneToOneField(User, on_delete=m.CASCADE, db_index=True, editable=False, verbose_name='Пользователь')

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Активность пользователя'
        verbose_name_plural = 'Активность пользователей'


class PersonalInformation(m.Model):
    image = m.ImageField(upload_to=ICONS_PATH_UPLOAD, null=True, blank=True, verbose_name='Аватарка')
    cover_image = m.ImageField(upload_to=IMAGES_PATH_UPLOAD, null=True, blank=True, verbose_name='Обложка')
    birthday = m.DateField(verbose_name='Дата дня рождения', null=True, blank=True, validators=(validate_past_date,))
    about_me = m.CharField(max_length=ABOUT_ME_MAX_LENGTH, null=True, blank=True, verbose_name='О себе')

    user = m.OneToOneField(User, on_delete=m.CASCADE, db_index=True, editable=False, verbose_name='Пользователь')

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse('user', args=(self.user.id,))

    class Meta:
        verbose_name = 'Личная информация'
        verbose_name_plural = 'Личная информация'
        ordering = ['-birthday']


class IntegrationTelegram(m.Model):
    telegram_username = m.CharField(max_length=URL_MAX_LENGTH, null=True, blank=True,
                                    verbose_name='Никнейм в Telegram')
    connect = m.BooleanField(default=False, verbose_name='Подключить')
    connection_status = m.BooleanField(default=False, verbose_name='Статус подключения')

    user = m.OneToOneField(User, on_delete=m.CASCADE, db_index=True, verbose_name='Пользователь')

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Интеграция с Telegram'
        verbose_name_plural = 'Интеграции с Telegram'


class UserSettings(m.Model):
    dark_theme = m.BooleanField(default=False, verbose_name='Темная тема')
    background_image = m.ImageField(upload_to=IMAGES_PATH_UPLOAD, null=True, blank=True,
                                    verbose_name='Фоновое изображение')

    user = m.OneToOneField(User, on_delete=m.CASCADE, db_index=True, verbose_name='Пользователь')

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse('edit-user', args=(self.user.id,))

    class Meta:
        verbose_name = 'Настройки пользователя'
        verbose_name_plural = 'Настройки пользователя'


class HappyBirthday(m.Model):
    age = m.PositiveIntegerField(verbose_name='Возраст')

    personal_information = m.ForeignKey(PersonalInformation, on_delete=m.CASCADE, verbose_name='Личная информация')

    def __str__(self):
        return str(self.personal_information.user) + ' - ' + str(self.age)

    class Meta:
        verbose_name = 'Поздравление с днем рождения'
        verbose_name_plural = 'Поздравления с днем рождения'


class UserVerification(m.Model):
    rejected = m.BooleanField(default=False, verbose_name='Отклонено')
    rejection_cause = m.CharField(max_length=MESSAGE_MAX_LENGTH, null=True, blank=True,
                                  verbose_name='Причина отклонения')

    user = m.OneToOneField(User, on_delete=m.CASCADE, db_index=True, verbose_name='Пользователь')

    def __str__(self):
        return str(self.user) + (' (Отклонен)' if self.rejected else ' (Принят)')

    class Meta:
        verbose_name = 'Верификация пользователя'
        verbose_name_plural = 'Верификация пользователей'
        ordering = ['rejected']


class HashtagList(m.Model):
    def __str__(self):
        return 'id=' + str(self.id)

    class Meta:
        verbose_name = 'Список хештегов'
        verbose_name_plural = 'Списки хештегов'


class Hashtag(m.Model):
    name = m.CharField(max_length=HEADER_MAX_LENGTH, db_index=True, unique=True, verbose_name='Название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Хештег'
        verbose_name_plural = 'Хештег'


class HashtagFromList(m.Model):
    hashtag = m.ForeignKey(Hashtag, on_delete=m.CASCADE, editable=False, verbose_name='Хештег')
    hashtag_list = m.ForeignKey(HashtagList, on_delete=m.CASCADE, editable=False, verbose_name='Список хештегов')

    def __str__(self):
        return str(self.hashtag) + ' - ' + str(self.hashtag_list)

    class Meta:
        verbose_name = 'Хештег из списка'
        verbose_name_plural = 'Хештеги из списков'


class CommentList(m.Model):
    def __str__(self):
        return 'id=' + str(self.id)

    class Meta:
        verbose_name = 'Список комментариев'
        verbose_name_plural = 'Списки комментариев'


class Comment(m.Model):
    datetime_create = m.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    text = m.TextField(max_length=MESSAGE_MAX_LENGTH, verbose_name='Текст')
    is_read = m.BooleanField(default=False, verbose_name='Прочитано')

    comment_list = m.ForeignKey(CommentList, on_delete=m.CASCADE, editable=False, verbose_name='Список комментариев')
    user = m.ForeignKey(User, on_delete=m.CASCADE, verbose_name='Пользователь')
    nested_comment = m.ForeignKey('Comment', on_delete=m.SET_NULL, null=True, blank=True,
                                  verbose_name='Вложенный комментарий')

    def __str__(self):
        return str(self.user) + ' - ' + str(self.comment_list)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-datetime_create']


class Teacher(m.Model):
    user = m.OneToOneField(User, on_delete=m.CASCADE, db_index=True, verbose_name='Пользователь')

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse('user', args=(self.user.id,))

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'


class StudentGroup(m.Model):
    name = m.CharField(max_length=NAME_MAX_LENGTH, unique=True, verbose_name='Название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Группа студентов'
        verbose_name_plural = 'Группы студентов'
        ordering = ['name']


class Level(m.Model):
    value = m.PositiveIntegerField(unique=True, db_index=True, verbose_name='Значение')
    points = m.PositiveIntegerField(unique=True, verbose_name='Количество баллов')

    def __str__(self):
        return str(self.value)

    class Meta:
        verbose_name = 'Уровень'
        verbose_name_plural = 'Уровни'


class Rank(m.Model):
    name = m.CharField(max_length=NAME_MAX_LENGTH, unique=True, verbose_name='Название')
    code = m.PositiveIntegerField(unique=True, db_index=True, editable=False, verbose_name='Код')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ранг'
        verbose_name_plural = 'Ранг'
        ordering = ['code']


class Student(m.Model):
    points = m.PositiveIntegerField(default=0, verbose_name='Количество баллов')
    coins = m.PositiveIntegerField(default=0, verbose_name='Количество монет')
    option = m.PositiveIntegerField(null=True, blank=True, verbose_name='Вариант')

    user = m.OneToOneField(User, on_delete=m.CASCADE, db_index=True, verbose_name='Пользователь')
    group = m.ForeignKey(StudentGroup, on_delete=m.CASCADE, verbose_name='Группа')
    level = m.ForeignKey(Level, on_delete=m.PROTECT, verbose_name='Уровень')
    rank = m.ForeignKey(Rank, on_delete=m.PROTECT, verbose_name='Ранг')

    def get_absolute_url(self):
        return reverse('user', args=(self.user.username,))

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'


class StudentActivity(m.Model):
    pass_tasks_first_time_in_a_row = m.PositiveIntegerField(
        default=0, verbose_name='Выполнено заданий с первого раза подряд')
    pass_tasks_first_time_in_a_row_max = m.PositiveIntegerField(
        default=0, verbose_name='Выполнено заданий с первого раза подряд максимум')

    student = m.OneToOneField(Student, on_delete=m.CASCADE, db_index=True, editable=False, verbose_name='Студент')

    def __str__(self):
        return str(self.student)

    class Meta:
        verbose_name = 'Активность студента'
        verbose_name_plural = 'Активности студентов'


class ProjectStatus(m.Model):
    name = m.CharField(max_length=HEADER_MAX_LENGTH, null=True, blank=True, verbose_name='Название')
    code = m.PositiveIntegerField(unique=True, db_index=True, editable=False, verbose_name='Код')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Статус проекта'
        verbose_name_plural = 'Статусы проектов'


class Project(m.Model):
    name = m.CharField(max_length=HEADER_MAX_LENGTH, null=True, blank=True, verbose_name='Название')
    document_url = m.CharField(max_length=URL_MAX_LENGTH, null=True, blank=True,
                               verbose_name='Ссылка на Google Document',
                               validators=(URLValidator(), validate_document_url))
    figma_url = m.CharField(max_length=URL_MAX_LENGTH, null=True, blank=True,
                            verbose_name='Ссылка на Figma',
                            validators=(URLValidator(), validate_figma_url))
    drawio_url = m.CharField(max_length=URL_MAX_LENGTH, null=True, blank=True,
                             verbose_name='Ссылка на Drawio',
                             validators=(URLValidator(), validate_drawio_url))
    github_url = m.CharField(max_length=URL_MAX_LENGTH, null=True, blank=True,
                             verbose_name='Ссылка на GitHub',
                             validators=(URLValidator(), validate_github_url))

    student = m.OneToOneField(Student, on_delete=m.CASCADE, db_index=True, verbose_name='Студент')
    status = m.ForeignKey(ProjectStatus, on_delete=m.PROTECT, verbose_name='Статус')
    comment_list = m.OneToOneField(CommentList, on_delete=m.SET_NULL, null=True, blank=True, editable=False,
                                   verbose_name='Список комментариев')

    def get_absolute_url(self):
        return reverse('project', args=(self.id,))

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'


class Lesson(m.Model):
    name = m.CharField(max_length=HEADER_MAX_LENGTH, null=True, blank=True, verbose_name='Название')
    date = m.DateField(verbose_name='Дата')
    number = m.PositiveIntegerField(verbose_name='Номер занятия')

    student_group = m.ForeignKey(StudentGroup, on_delete=m.CASCADE, verbose_name='Группа студентов')

    def __str__(self):
        return str(self.date) + (' - ' + self.name if self.name else '')

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'
        ordering = ['-date']


class LessonPresence(m.Model):
    student = m.ForeignKey(Student, on_delete=m.CASCADE, verbose_name='Студент')
    lesson = m.ForeignKey(Lesson, on_delete=m.CASCADE, verbose_name='Занятие')

    def __str__(self):
        return str(self.student) + ' - ' + str(self.lesson)

    class Meta:
        verbose_name = 'Присутствие на занятии'
        verbose_name_plural = 'Присутствия на занятиях'
        ordering = ['-lesson__date']


class Feedback(m.Model):
    datetime_create = m.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    text = m.TextField(max_length=MESSAGE_MAX_LENGTH, verbose_name='Текст')
    is_read = m.BooleanField(default=False, verbose_name='Прочитано')

    student_group = m.ForeignKey(StudentGroup, null=True, blank=True, on_delete=m.SET_NULL,
                                 verbose_name='Группа студентов')

    def __str__(self):
        return get_cropped_text(self.text, max_size=ADMIN_CROPPED_TEXT_SIZE)

    def get_absolute_url(self):
        return reverse('feedback')

    class Meta:
        verbose_name = 'Обратная связь'
        verbose_name_plural = 'Обратная связь'
        ordering = ['is_read']


class PointsAdditional(m.Model):
    date_receiving = m.DateField(verbose_name='Дата получения')
    points = m.PositiveIntegerField(default=0, verbose_name='Количество баллов')
    comment = m.CharField(max_length=MESSAGE_MAX_LENGTH, null=True, blank=True, verbose_name='Комментарий')

    student = m.ForeignKey(Student, on_delete=m.CASCADE, verbose_name='Студент')

    def __str__(self):
        return '[' + str(self.date_receiving) + '] ' + str(self.student)

    class Meta:
        verbose_name = 'Дополнительные баллы'
        verbose_name_plural = 'Дополнительные баллы'
        ordering = ['-date_receiving']


class AchievementProgressScript(m.Model):
    name = m.CharField(max_length=NAME_MAX_LENGTH, unique=True, verbose_name='Имя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Скрипт получения прогресса достижения'
        verbose_name_plural = 'Скрипты получения прогресса достижения'


class Achievement(m.Model):
    icon_name = m.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True, verbose_name='Название иконки')
    name = m.CharField(max_length=HEADER_MAX_LENGTH, unique=True, verbose_name='Название')
    description = m.TextField(max_length=MESSAGE_MAX_LENGTH, null=True, blank=True, verbose_name='Описание')
    is_private = m.BooleanField(default=False, verbose_name='Личное')
    is_systemic = m.BooleanField(default=False, editable=False, verbose_name='Системное')
    code = m.PositiveIntegerField(db_index=True, default=None, null=True, blank=True, editable=False,
                                  verbose_name='Код')

    progress_script = m.ForeignKey(AchievementProgressScript, on_delete=m.SET_NULL, null=True, blank=True,
                                   verbose_name='Скрипт получения прогресса')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('achievements')

    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'
        ordering = ['code']


class AchievementLevel(m.Model):
    name = m.CharField(max_length=HEADER_MAX_LENGTH, null=True, blank=True, verbose_name='Название')
    description = m.TextField(max_length=MESSAGE_MAX_LENGTH, null=True, blank=True, verbose_name='Описание')
    level = m.PositiveIntegerField(verbose_name='Уровень', validators=(MinValueValidator(1),))
    required_value = m.IntegerField(null=True, blank=True, verbose_name='Необходимое значение')
    badge_awarded = m.BooleanField(default=False, verbose_name='Выдается значок')

    achievement = m.ForeignKey(Achievement, on_delete=m.CASCADE, verbose_name='Достижение')
    rank = m.ForeignKey(Rank, on_delete=m.PROTECT, verbose_name='Ранг')

    def __str__(self):
        return self.achievement.name + ' - ' + str(self.level) + ' ур.'

    class Meta:
        verbose_name = 'Уровень достижения'
        verbose_name_plural = 'Уровни достижений'
        ordering = ['rank__code']


class StudentAchievement(m.Model):
    date_receiving = m.DateField(verbose_name='Дата получения')
    level = m.PositiveIntegerField(default=1, verbose_name='Уровень',
                                   validators=(MinValueValidator(1),))
    viewed = m.BooleanField(default=False, verbose_name='Просмотрено')

    student = m.ForeignKey(Student, on_delete=m.CASCADE, verbose_name='Студент')
    achievement = m.ForeignKey(Achievement, on_delete=m.CASCADE, verbose_name='Достижение')

    def __str__(self):
        return str(self.student) + ' - \"' + str(self.achievement) + '\" ' + str(self.level)

    def get_absolute_url(self):
        return reverse('achievements')

    class Meta:
        verbose_name = 'Достижение студента'
        verbose_name_plural = 'Достижения студентов'
        ordering = ['-date_receiving']


class CourseSection(m.Model):
    image = m.ImageField(upload_to=ICONS_PATH_UPLOAD, null=True, blank=True, verbose_name='Иконка')
    name = m.CharField(max_length=HEADER_MAX_LENGTH, unique=True, verbose_name='Название')
    position = m.PositiveIntegerField(default=0, verbose_name='Позиция в списке')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Раздел курса'
        verbose_name_plural = 'Разделы курса'


class Difficulty(m.Model):
    name = m.CharField(max_length=NAME_MAX_LENGTH, unique=True, verbose_name='Название')
    code = m.PositiveIntegerField(unique=True, db_index=True, editable=False, verbose_name='Код')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Сложность'
        verbose_name_plural = 'Сложности'
        ordering = ['code']


class AnswerFormat(m.Model):
    name = m.CharField(max_length=NAME_MAX_LENGTH, unique=True, verbose_name='Название')
    code = m.PositiveIntegerField(unique=True, db_index=True, editable=False, verbose_name='Код')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Формат ответа'
        verbose_name_plural = 'Форматы ответов'
        ordering = ['code']


class FileList(m.Model):
    def __str__(self):
        return 'id=' + str(self.id)

    class Meta:
        verbose_name = 'Список файлов'
        verbose_name_plural = 'Списки файлов'


class File(m.Model):
    datetime_create = m.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    file = m.FileField(upload_to=FILES_PATH_UPLOAD, verbose_name='Файл')

    file_list = m.ForeignKey(FileList, on_delete=m.CASCADE, verbose_name='Список файлов')

    def __str__(self):
        return self.file.name

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'
        ordering = ['-datetime_create']


class Task(m.Model):
    datetime_create = m.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    image = m.ImageField(upload_to=ICONS_PATH_UPLOAD, null=True, blank=True, verbose_name='Иконка')
    name = m.CharField(max_length=HEADER_MAX_LENGTH, verbose_name='Название')
    text = m.TextField(max_length=TEXT_MAX_LENGTH, verbose_name='Текст задачи')
    answer_after_complete = m.TextField(null=True, blank=True, verbose_name='Ответ после выполнения')
    points = m.PositiveIntegerField(default=0, verbose_name='Баллы за выполнение')

    max_attempts = m.PositiveIntegerField(null=True, blank=True, verbose_name='Максимальное количество попыток')
    attempts_per_day = m.PositiveIntegerField(null=True, blank=True, verbose_name='Количество попыток в день')
    manual_check_result = m.BooleanField(default=True, verbose_name='Ручная проверка выполнения')

    count_forms = m.PositiveIntegerField(default=1, verbose_name='Количество форм ввода')
    variable_count_forms = m.BooleanField(default=False, verbose_name='Изменяемое количество форм ввода')

    course_section = m.ForeignKey(CourseSection, on_delete=m.CASCADE, verbose_name='Раздел')
    difficulty = m.ForeignKey(Difficulty, on_delete=m.SET_NULL, null=True, blank=True, verbose_name='Сложность')
    answer_format = m.ForeignKey(AnswerFormat, on_delete=m.PROTECT, verbose_name='Формат ответа')
    hashtag_list = m.OneToOneField(HashtagList, on_delete=m.SET_NULL, null=True, blank=True, editable=False,
                                   verbose_name='Список хештегов')
    comment_list = m.OneToOneField(CommentList, on_delete=m.SET_NULL, null=True, blank=True, editable=False,
                                   verbose_name='Список комментариев')
    file_list = m.OneToOneField(FileList, on_delete=m.SET_NULL, null=True, blank=True, editable=False,
                                verbose_name='Список файлов')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('task', args=(self.id,))

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        ordering = ['-datetime_create']


class AssignedTask(m.Model):
    datetime_create = m.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    readline = m.DateTimeField(null=True, blank=True, verbose_name='Мягкий срок выполнения')
    deadline = m.DateTimeField(null=True, blank=True, verbose_name='Жесткий срок выполнения')

    task = m.ForeignKey(Task, on_delete=m.CASCADE, verbose_name='Задание')
    student_group = m.ForeignKey(StudentGroup, on_delete=m.CASCADE, verbose_name='Группа студентов')

    def __str__(self):
        return '[' + datetime_to_string(datetime_timezone(self.datetime_create)) + '] ' + \
               str(self.task) + ' - ' + str(self.student_group)

    def get_absolute_url(self):
        return reverse('task', args=(self.task.id,))

    class Meta:
        verbose_name = 'Назначенное задание'
        verbose_name_plural = 'Назначенные задания'
        ordering = ['-deadline', '-readline']


class TaskStatus(m.Model):
    name = m.CharField(max_length=NAME_MAX_LENGTH, unique=True, verbose_name='Название')
    code = m.PositiveIntegerField(unique=True, db_index=True, editable=False, verbose_name='Код')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Статус выполнения задания'
        verbose_name_plural = 'Статусы выполнения заданий'
        ordering = ['code']


class CompletingTask(m.Model):
    datetime_sent = m.DateTimeField(null=True, blank=True, verbose_name='Дата и время отправления')
    total_attempts = m.PositiveIntegerField(default=0, verbose_name='Всего попыток')
    attempts_today = m.PositiveIntegerField(default=0, verbose_name='Попыток сегодня')
    kwargs = m.JSONField(max_length=TEXT_MAX_LENGTH, null=True, blank=True, verbose_name='Словарь аргументов')
    points = m.PositiveIntegerField(default=0, verbose_name='Баллы за выполнение')
    viewed = m.BooleanField(default=False, verbose_name='Просмотрено')

    student = m.ForeignKey(Student, on_delete=m.CASCADE, verbose_name='Студент')
    assigned_task = m.ForeignKey(AssignedTask, on_delete=m.CASCADE, verbose_name='Назначенное задание')
    status = m.ForeignKey(TaskStatus, on_delete=m.PROTECT, verbose_name='Статус')
    comment_list = m.OneToOneField(CommentList, on_delete=m.SET_NULL, null=True, blank=True, editable=False,
                                   verbose_name='Список комментариев')
    file_list = m.OneToOneField(FileList, on_delete=m.SET_NULL, null=True, blank=True, editable=False,
                                verbose_name='Список файлов')

    def __str__(self):
        return str(self.student) + ' - \"' + str(self.assigned_task) + '\"'

    def get_absolute_url(self):
        return reverse('task', args=(self.assigned_task.task.id,))

    class Meta:
        verbose_name = 'Выполнение задания'
        verbose_name_plural = 'Выполнения заданий'
        ordering = ['-datetime_sent']


class TaskAccessCheckScript(m.Model):
    icon_name = m.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True, verbose_name='Название иконки')
    name = m.CharField(max_length=NAME_MAX_LENGTH, unique=True, verbose_name='Имя')
    description = m.CharField(max_length=MESSAGE_MAX_LENGTH, verbose_name='Описание')
    kwargs = m.JSONField(max_length=TEXT_MAX_LENGTH, null=True, blank=True, verbose_name='Словарь аргументов')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Скрипт проверки доступа к заданию'
        verbose_name_plural = 'Скрипты проверки доступа к заданиям'


class CheckingTaskAccess(m.Model):
    kwargs = m.JSONField(max_length=TEXT_MAX_LENGTH, null=True, blank=True, verbose_name='Словарь аргументов')

    task = m.ForeignKey(Task, on_delete=m.CASCADE, verbose_name='Задание')
    script = m.ForeignKey(TaskAccessCheckScript, on_delete=m.CASCADE, verbose_name='Скрипт')

    def __str__(self):
        return str(self.task) + ' - ' + str(self.script)

    class Meta:
        verbose_name = 'Проверка доступа к заданию'
        verbose_name_plural = 'Проверки доступа к заданию'


class CompletingTaskCheckScript(m.Model):
    icon_name = m.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True, verbose_name='Название иконки')
    name = m.CharField(max_length=NAME_MAX_LENGTH, unique=True, verbose_name='Имя')
    description = m.CharField(max_length=MESSAGE_MAX_LENGTH, verbose_name='Описание')
    kwargs = m.JSONField(max_length=TEXT_MAX_LENGTH, null=True, blank=True, verbose_name='Словарь аргументов')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Скрипт проверки выполнения задания'
        verbose_name_plural = 'Скрипты проверки выполнения заданий'


class CheckingCompletingTask(m.Model):
    kwargs = m.JSONField(max_length=TEXT_MAX_LENGTH, null=True, blank=True, verbose_name='Словарь аргументов')
    on_a_background = m.BooleanField(default=False, verbose_name='Фоновое выполнение')

    task = m.ForeignKey(Task, on_delete=m.CASCADE, verbose_name='Задание')
    script = m.ForeignKey(CompletingTaskCheckScript, on_delete=m.CASCADE, verbose_name='Скрипт')

    def __str__(self):
        return str(self.task) + ' - ' + str(self.script)

    class Meta:
        verbose_name = 'Проверка выполнения задания'
        verbose_name_plural = 'Проверки выполнения заданий'


class ProcCheckingCompletingTask(m.Model):
    completing_task = m.ForeignKey(CompletingTask, on_delete=m.CASCADE, verbose_name='Назначенное задание')
    checking_completing_task = m.ForeignKey(CheckingCompletingTask, on_delete=m.CASCADE,
                                            verbose_name='Проверка выполнения задания')

    def __str__(self):
        return str(self.completing_task) + ' - ' + str(self.checking_completing_task)

    class Meta:
        verbose_name = 'Обработка проверки выполнения задания'
        verbose_name_plural = 'Обработка проверок выполнения заданий'


class Test(m.Model):
    datetime_create = m.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    image = m.ImageField(upload_to=ICONS_PATH_UPLOAD, null=True, blank=True, verbose_name='Иконка')
    name = m.CharField(max_length=HEADER_MAX_LENGTH, verbose_name='Название')
    text = m.TextField(max_length=TEXT_MAX_LENGTH, verbose_name='Текст')
    points = m.PositiveIntegerField(default=0, verbose_name='Количество баллов')
    time = m.TimeField(null=True, blank=True, verbose_name='Время на прохождение')
    shuffle_order_tasks = m.BooleanField(default=False, verbose_name='Перемешать порядок заданий')
    shuffle_order_answers = m.BooleanField(default=False, verbose_name='Перемешать порядок ответов')
    enable_points = m.BooleanField(default=True, verbose_name='Включить баллы')

    course_section = m.ForeignKey(CourseSection, on_delete=m.CASCADE, null=True, blank=True,
                                  verbose_name='Раздел курса')
    comment_list = m.OneToOneField(CommentList, on_delete=m.SET_NULL, null=True, blank=True, editable=False,
                                   verbose_name='Список комментариев')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('test', args=(self.id,))

    class Meta:
        verbose_name = 'Тестирование'
        verbose_name_plural = 'Тестирования'
        ordering = ['-datetime_create']


class AssignedTest(m.Model):
    date = m.DateField(verbose_name='Назначенная дата')
    is_open = m.BooleanField(default=False, verbose_name='Доступно для выполнения')
    open_results = m.BooleanField(default=False, verbose_name='Открыть результаты')

    test = m.ForeignKey(Test, on_delete=m.CASCADE, verbose_name='Тестирование')
    student_group = m.ForeignKey(StudentGroup, on_delete=m.CASCADE, verbose_name='Группа студентов')

    def __str__(self):
        return '[' + str(self.date) + '] ' + str(self.test) + ' - ' + str(self.student_group)

    def get_absolute_url(self):
        return reverse('test', args=(self.test.id,))

    class Meta:
        verbose_name = 'Назначенное тестирование'
        verbose_name_plural = 'Назначенные тестирование'
        ordering = ['-date']


class TestResult(m.Model):
    datetime_begin = m.DateTimeField(verbose_name='Дата и время начала')
    datetime_complete = m.DateTimeField(null=True, blank=True, verbose_name='Дата и время завершения')
    points = m.PositiveIntegerField(default=0, verbose_name='Количество баллов')
    penalty_points = m.PositiveIntegerField(default=0, verbose_name='Штрафные баллы')
    viewed = m.BooleanField(default=False, verbose_name='Просмотрено')
    completed = m.BooleanField(default=False, verbose_name='Завершено')

    assigned_test = m.ForeignKey(AssignedTest, on_delete=m.CASCADE, verbose_name='Назначенное тестирование')
    student = m.ForeignKey(Student, on_delete=m.CASCADE, verbose_name='Студент')

    def __str__(self):
        return str(self.student) + ' - \"' + str(self.assigned_test) + '\"'

    def get_absolute_url(self):
        return reverse('test', args=(self.assigned_test.test.id,))

    class Meta:
        verbose_name = 'Результат тестирования'
        verbose_name_plural = 'Результаты тестирований'
        ordering = ['-datetime_complete', '-assigned_test__date', '-points']


class TestSection(m.Model):
    name = m.CharField(max_length=HEADER_MAX_LENGTH, verbose_name='Название')
    description = m.TextField(max_length=MESSAGE_MAX_LENGTH, null=True, blank=True, verbose_name='Описание')
    position = m.PositiveIntegerField(default=0, verbose_name='Позиция в списке')

    test = m.ForeignKey(Test, on_delete=m.CASCADE, verbose_name='Тестирование')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Раздел в тестировании'
        verbose_name_plural = 'Разделы в тестированиях'


class TestTask(m.Model):
    text = m.CharField(max_length=MESSAGE_MAX_LENGTH, verbose_name='Текст')
    image = m.ImageField(upload_to=IMAGES_PATH_UPLOAD, null=True, blank=True, verbose_name='Изображение')
    points = m.PositiveIntegerField(default=1, verbose_name='Количество баллов')
    position = m.PositiveIntegerField(default=0, verbose_name='Позиция в списке')
    required = m.BooleanField(default=False, verbose_name='Обязательный')

    test = m.ForeignKey(Test, on_delete=m.CASCADE, verbose_name='Тестирование')
    test_section = m.ForeignKey(TestSection, null=True, blank=True, on_delete=m.CASCADE,
                                verbose_name='Раздел в тестировании')

    def __str__(self):
        return str(self.test) + ' - ' + str(self.position)

    class Meta:
        verbose_name = 'Задание в тестировании'
        verbose_name_plural = 'Задание в тестировании'


class TestTaskAnswer(m.Model):
    text = m.TextField(max_length=MESSAGE_MAX_LENGTH, null=True, blank=True, verbose_name='Текст')
    points = m.PositiveIntegerField(default=0, verbose_name='Количество баллов')
    verified = m.BooleanField(default=False, verbose_name='Проверено')

    test_task = m.ForeignKey(TestTask, on_delete=m.CASCADE, verbose_name='Задание в тестировании')
    student = m.ForeignKey(Student, on_delete=m.CASCADE, verbose_name='Студент')

    def __str__(self):
        return str(self.test_task) + ' - ' + get_cropped_text(self.text, max_size=ADMIN_CROPPED_TEXT_SIZE)

    class Meta:
        verbose_name = 'Ответ на задание в тестировании'
        verbose_name_plural = 'Ответы на задания в тестировании'


class TestTextAnswer(m.Model):
    correct_answer = m.TextField(max_length=MESSAGE_MAX_LENGTH, null=True, blank=True, verbose_name='Правильный ответ')
    multiline = m.BooleanField(default=False, verbose_name='Многострочный')

    test_task = m.OneToOneField(TestTask, on_delete=m.CASCADE, verbose_name='Задание в тестировании')

    def __str__(self):
        return str(self.test_task)

    class Meta:
        verbose_name = 'Текстовый ответ'
        verbose_name_plural = 'Текстовый ответ'


class TestCheckAnswerList(m.Model):
    one_answer = m.BooleanField(default=False, verbose_name='Один вариант ответа')

    test_task = m.OneToOneField(TestTask, on_delete=m.CASCADE, verbose_name='Задание в тестировании')

    def __str__(self):
        return str(self.test_task)

    class Meta:
        verbose_name = 'Список вариантов ответов'
        verbose_name_plural = 'Список вариантов ответов'


class TestCheckAnswer(m.Model):
    text = m.TextField(max_length=MESSAGE_MAX_LENGTH, verbose_name='Текст')
    position = m.PositiveIntegerField(default=0, verbose_name='Позиция в списке')
    is_correct = m.BooleanField(default=False, verbose_name='Правильный')

    possible_answer_list = m.ForeignKey(TestCheckAnswerList, on_delete=m.CASCADE,
                                        verbose_name='Список вариантов ответов')

    def __str__(self):
        return (str(self.possible_answer_list) + ' - ' +
                get_cropped_text(self.text, max_size=ADMIN_CROPPED_TEXT_SIZE) +
                (' [' + ('Да' if self.is_correct else 'Нет') + ']'))

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Вариант ответа'


class SelectedTestAnswer(m.Model):
    task_user_answer = m.ForeignKey(TestTaskAnswer, on_delete=m.CASCADE,
                                    verbose_name='Ответ на задание в тестировании')
    check_answer = m.ForeignKey(TestCheckAnswer, on_delete=m.CASCADE, verbose_name='Вариант ответа')

    def __str__(self):
        return str(self.task_user_answer) + ' - ' + str(self.check_answer)

    class Meta:
        verbose_name = 'Выбранный вариант ответа'
        verbose_name_plural = 'Выбранный вариант ответа'


class Event(m.Model):
    datetime_begin = m.DateTimeField(verbose_name='Дата и время начала')
    datetime_end = m.DateTimeField(verbose_name='Дата и время завершения')

    name = m.CharField(max_length=HEADER_MAX_LENGTH, verbose_name='Название')
    image = m.ImageField(upload_to=ICONS_PATH_UPLOAD, null=True, blank=True, verbose_name='Иконка')
    text = m.TextField(max_length=MESSAGE_MAX_LENGTH, null=True, blank=True, verbose_name='Описание')
    points = m.PositiveIntegerField(unique=True, verbose_name='Количество баллов')

    comment_list = m.OneToOneField(CommentList, on_delete=m.SET_NULL, null=True, blank=True, editable=False,
                                   verbose_name='Список комментариев')
    hashtag_list = m.OneToOneField(HashtagList, on_delete=m.SET_NULL, null=True, blank=True, editable=False,
                                   verbose_name='Список хештегов')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('event', args=(self.id,))

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'


class AssignedEvent(m.Model):
    datetime_begin = m.DateTimeField(null=True, blank=True, verbose_name='Дата и время начала')
    datetime_end = m.DateTimeField(null=True, blank=True, verbose_name='Дата и время завершения')

    event = m.ForeignKey(Event, on_delete=m.CASCADE, verbose_name='Событие')
    student_group = m.ForeignKey(StudentGroup, on_delete=m.CASCADE, verbose_name='Группа студентов')

    def __str__(self):
        return str(self.event) + ' - ' + str(self.student_group)

    def get_absolute_url(self):
        return reverse('event', args=(self.event.id,))

    class Meta:
        verbose_name = 'Событие для группы студентов'
        verbose_name_plural = 'События для групп студентов'
        ordering = ['-datetime_begin', 'datetime_end']


class Post(m.Model):
    datetime_create = m.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    datetime_update = m.DateTimeField(auto_now=True, verbose_name='Дата и время обновления')
    header = m.CharField(max_length=HEADER_MAX_LENGTH, unique=True, verbose_name='Заголовок')
    description = m.CharField(max_length=MESSAGE_MAX_LENGTH, null=True, blank=True, verbose_name='Описание')
    text = m.TextField(verbose_name='Текст')
    is_published = m.BooleanField(default=True, verbose_name='Опубликовать')
    count_views = m.PositiveIntegerField(default=0, editable=False, verbose_name='Количество просмотров')

    comment_list = m.OneToOneField(CommentList, on_delete=m.SET_NULL, null=True, blank=True, editable=False,
                                   verbose_name='Список комментариев')
    hashtag_list = m.OneToOneField(HashtagList, on_delete=m.SET_NULL, null=True, blank=True, editable=False,
                                   verbose_name='Список хештегов')
    file_list = m.OneToOneField(FileList, on_delete=m.SET_NULL, null=True, blank=True, editable=False,
                                verbose_name='Список файлов')

    def __str__(self):
        return self.header

    def get_absolute_url(self):
        return reverse('post', args=(self.id,))

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class PostForStudentGroup(m.Model):
    post = m.ForeignKey(Post, on_delete=m.CASCADE, verbose_name='Пост')
    student_group = m.ForeignKey(StudentGroup, on_delete=m.CASCADE, verbose_name='Группа студентов')

    def __str__(self):
        return str(self.post) + ' - ' + str(self.student_group)

    def get_absolute_url(self):
        return reverse('post', args=(self.post.id,))

    class Meta:
        verbose_name = 'Пост для группы студентов'
        verbose_name_plural = 'Посты для групп студентов'


class PostView(m.Model):
    post = m.ForeignKey(Post, on_delete=m.CASCADE, editable=False, verbose_name='Пост')
    user = m.ForeignKey(User, on_delete=m.CASCADE, editable=False, verbose_name='Пользователь')

    def __str__(self):
        return str(self.post) + ' - ' + str(self.user)

    class Meta:
        verbose_name = 'Просмотр поста'
        verbose_name_plural = 'Просмотры постов'
