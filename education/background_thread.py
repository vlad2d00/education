import datetime
import json
import os
import time
from threading import Thread

from dbbackup.settings import DATE_FORMAT

from api.db.config import TaskStatusCode
from api.db.dao import block_ip_address
from api.models import IPAddress, HappyBirthday, PersonalInformation, CompletingTask, ProcCheckingCompletingTask, \
    TaskStatus
from api.utils.completing_task_checks import CHECKING_COMPLETING_TASK_FUNC_BY_NAME
from api.utils.log import log_error
from api.utils.strings_storage import StringStorage
from education.backup import backup
from education.settings import BASE_DIR, DBBACKUP_FREQUENCY, BLOCKING_TIME_LIMIT_REQUESTS_PER_MINUTE, \
    REQUESTS_PER_MINUTE_LIMIT, MIN_TIME_FOR_BIRTHDAY_GREETINGS, BACKGROUND_THREAD_TICK
from education.utils.datetime_service import add_datetime, datetime_now


def background_thread():
    datetime_last_check_every_minute = None
    current_datetime = None

    def _check_completing_tasks():
        if not ProcCheckingCompletingTask.objects.exists():
            return

        items = ProcCheckingCompletingTask.objects.all().order_by('-id')
        for item in items:
            func = CHECKING_COMPLETING_TASK_FUNC_BY_NAME[item.checking_completing_task.script.name]

            # Если функция вернула None, то значит она будет вызвана повторно при следующей обработке
            result = func(item.completing_task, **item.checking_completing_task.kwargs)

            if result is False:
                item.completing_task.status = TaskStatus.objects.get(code=TaskStatusCode.TESTS_FAILED.value)
                # Удалим все назначенные проверки для этого выполнения задания
                for item_ in ProcCheckingCompletingTask.objects.filter(completing_task_id=item.completing_task.id):
                    item_.delete()
                break

            elif result is True:
                item.delete()

    def _check_ip_address_activity():
        for ip_address in IPAddress.objects.all():
            if ip_address.last_minute_requests > REQUESTS_PER_MINUTE_LIMIT:
                block_ip_address(ip_address_id=ip_address.id,
                                 datetime_unlock=add_datetime(datetime_now(),
                                                              seconds=BLOCKING_TIME_LIMIT_REQUESTS_PER_MINUTE),
                                 cause=StringStorage.EXCEED_LIMIT_COUNT_REQUESTS.value)

            ip_address.last_minute_requests = 0
            ip_address.save()

    def _check_backup():
        settings_file_name = os.path.join(BASE_DIR, 'backup', 'settings.json')
        if os.path.exists(settings_file_name):
            with open(settings_file_name, 'r') as f:
                settings = json.loads(f.read())

            datetime_last_backup = datetime.datetime.strptime(settings['datetime_last_backup'], DATE_FORMAT)
            total_seconds = (datetime_now().replace(tzinfo=None) - datetime_last_backup).total_seconds()
        else:
            settings = {}
            total_seconds = 10e9

        if total_seconds > DBBACKUP_FREQUENCY.total_seconds():
            backup(compress=True)
            with open(settings_file_name, 'w') as f:
                settings['datetime_last_backup'] = datetime_now().strftime(DATE_FORMAT)
                f.write(json.dumps(settings))

    def _check_happy_birthday():
        if not hasattr(_check_happy_birthday, 'datetime_last_check'):
            _check_happy_birthday.datetime_last_check = None

        # Если настало время проверки дня рождения у пользователей (раз в день в заданное время)
        if ((not _check_happy_birthday.datetime_last_check or
                _check_happy_birthday.datetime_last_check != current_datetime.date()) and
                current_datetime.time() >= MIN_TIME_FOR_BIRTHDAY_GREETINGS):

            for personal_information in PersonalInformation.objects.all():
                # Если у пользователя сегодня день рождения
                # и для него еще не было создано поздравление с исполнившемуся ему сегодня количеству лет
                if (personal_information.birthday == current_datetime.date() and
                        not HappyBirthday.objects.filter(personal_information_id=personal_information.id)):

                    age = current_datetime.date().year - personal_information.birthday.year
                    HappyBirthday.objects.create(personal_information_id=personal_information.id, age=age)

    def _check_completing_tasks_attempts():
        for task_complete in CompletingTask.objects.all():
            if task_complete.attempts_today > 0:
                task_complete.attempts_today = 0
                task_complete.save()

    def _every_tick():
        """
        Делать каждый тик, равный BACKGROUND_THREAD_TICK
        """
        _check_completing_tasks()

    def _every_minute():
        """
        Делать каждую минуту
        """
        _check_ip_address_activity()
        _check_backup()
        _check_happy_birthday()

    def _once_a_day():
        """
        Делать раз в день
        """
        _check_completing_tasks_attempts()

    date_last_check = None
    start_time = time.time()
    while True:
        try:
            current_datetime = datetime_now()

            _every_tick()

            if (not datetime_last_check_every_minute or
                    (datetime_last_check_every_minute - current_datetime).total_seconds() > 60):
                datetime_last_check_every_minute = current_datetime
                _every_minute()

            if not date_last_check or date_last_check != current_datetime.date():
                date_last_check = current_datetime.date()
                _once_a_day()

        except Exception as e:
            log_error(module_name=__name__, msg=str(e))

        delta_time = time.time() - start_time
        if delta_time < BACKGROUND_THREAD_TICK:
            time.sleep(BACKGROUND_THREAD_TICK - delta_time)

        start_time = time.time()


def start_background_thread():
    Thread(target=background_thread, daemon=True).start()
