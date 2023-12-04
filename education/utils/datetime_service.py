import datetime

from django.utils import timezone

TIME_ZONE = 3
DATETIME_ZERO = datetime.datetime(1900, 1, 1, 0, 0, 0)
DATETIME_EPS = 10


def datetime_now() -> datetime.datetime:
    return datetime.datetime.now(tz=timezone.utc)


def datetime_timezone(dt: datetime.datetime) -> datetime.datetime:
    return add_datetime(dt, hours=TIME_ZONE)


def datetime_timezone_now() -> datetime.datetime:
    return datetime_timezone(datetime.datetime.now(tz=timezone.utc))


def add_datetime(dt: datetime.datetime,
                 days: int = 0,
                 hours: int = 0,
                 minutes: int = 0,
                 seconds: int = 0
                 ) -> datetime:
    return dt + datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def subtract_datetime(
        dt: datetime.datetime,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0
) -> datetime:
    return dt + datetime.timedelta(days=-days, hours=-hours, minutes=-minutes, seconds=-seconds)


def time_to_seconds(tm: datetime.time) -> float:
    return tm.hour * 3600 + tm.minute * 60 + tm.second + float(tm.microsecond) / 1e6


def seconds_to_time(seconds: float) -> datetime.time:
    return datetime.time(int(seconds / 3600), int(seconds / 60), int(seconds), int(seconds * 1e6))


def datetime_to_string(
        dt: datetime.datetime,
        show_seconds: bool = True,
        accuracy: int = 0,
        sep_date: str = '-',
        sep_ms: str = '.',
        reverse_date: bool = False
) -> str:
    return date_to_string(dt.date(), sep=sep_date, reverse=reverse_date) + ' ' + \
           time_to_string(dt.time(), show_seconds=show_seconds, sep_ms=sep_ms, accuracy=accuracy)


def datetime_to_string_words(
        dt: datetime.datetime,
        show_seconds: bool = False,
        accuracy: int = 0,
        show_day_week: bool = False
) -> str:
    return (date_to_string_words(dt.date(),
                                 show_day_week=show_day_week,
                                 show_year=dt.date().year != datetime_now().year) + ' в ' +
            time_to_string(dt.time(),
                           show_seconds=show_seconds,
                           accuracy=accuracy))


def datetime_to_string_relative(
        dt_target: datetime.datetime,
        dt_original: datetime.datetime = None,
        show_day_week: bool = False,
        show_words: bool = False,
        fixed_time: bool = False,
        fixed_date: bool = False,
) -> str:
    if not dt_original:
        dt_original = datetime_now()

    in_past = dt_original > dt_target
    seconds = abs((dt_target - dt_original).total_seconds())

    if not fixed_time and seconds < DATETIME_EPS:
        return 'сейчас'

    format_ = '{value} {unit}.'
    if show_words:
        if in_past:
            format_ = format_ + ' назад'
        else:
            format_ = 'через ' + format_

    if not fixed_time and seconds < 86400:
        if seconds < 0.001:
            return format_.format(value=int(seconds * 1e6), unit='мкс')

        elif seconds < 1.0:
            return format_.format(value=int(seconds * 1e3), unit='мс')

        if seconds < 60:
            return format_.format(value=int(seconds), unit='сек')

        elif seconds < 3600:
            return format_.format(value=int(seconds // 60), unit='мин')

        else:
            return format_.format(value=int(seconds // 3600), unit='час')

    if fixed_time or fixed_date:
        days = abs((dt_target.date() - dt_original.date()).days)
        if not days and fixed_time:
            words = 'сегодня в ' if show_words else ''
            return words + time_to_string(dt_target.time(), show_seconds=False)

        elif days < 2:
            if show_words:
                if not days:
                    words = 'сегодня в '
                elif in_past:
                    words = 'вчера в '
                else:
                    words = 'завтра в '
            else:
                words = ''

            return words + time_to_string(dt_target.time(), show_seconds=False)

        else:
            return (date_to_string_words(dt_target,
                                         show_day_week=show_day_week,
                                         show_year=(dt_target.year != dt_original.year)) + ' в ' +
                    time_to_string(dt_target.time(), show_seconds=False))

    else:
        days = int(seconds // 86400)
        return format_.format(value=days, unit='дн')


def date_to_string(date: datetime.date, sep: str = '-', reverse: bool = False) -> str:
    if reverse:
        return date.strftime(f'%d{sep}%m{sep}%Y')
    else:
        return date.strftime(f'%Y{sep}%m{sep}%d')


def date_to_string_words(date: datetime.date, show_day_week: bool = False, show_year: bool = True) -> str:
    return str(date.day) + ' ' + \
           month_to_string(date.month) + '.' + \
           (' ' + str(date.year) + ' года' if show_year else '') + \
           (' (' + day_week_to_string(date.weekday()) + ')' if show_day_week else '')


def time_to_string(
        time: datetime.time,
        show_seconds: bool = True,
        sep_ms: str = '.',
        accuracy: int = 0
) -> str:
    if show_seconds:
        if accuracy > 0:
            ms = round(round(time.microsecond / 1e6, accuracy) * (10 ** accuracy))
            return time.strftime('%H:%M:%S' + sep_ms + str(ms))
        else:
            return time.strftime('%H:%M:%S')
    else:
        return time.strftime('%H:%M')


def month_to_string(month_number: int) -> str:
    if month_number == 1:
        return 'янв'
    elif month_number == 2:
        return 'фев'
    elif month_number == 3:
        return 'мар'
    elif month_number == 4:
        return 'апр'
    elif month_number == 5:
        return 'май'
    elif month_number == 6:
        return 'июн'
    elif month_number == 7:
        return 'июл'
    elif month_number == 8:
        return 'авг'
    elif month_number == 9:
        return 'сен'
    elif month_number == 10:
        return 'окт'
    elif month_number == 11:
        return 'ноя'
    elif month_number == 12:
        return 'дек'
    else:
        return '?'


def day_week_to_string(month_number: int) -> str:
    if month_number == 0:
        return 'пн'
    elif month_number == 1:
        return 'вт'
    elif month_number == 2:
        return 'ср'
    elif month_number == 3:
        return 'чт'
    elif month_number == 4:
        return 'пт'
    elif month_number == 5:
        return 'сб'
    elif month_number == 6:
        return 'вс'
    else:
        return '?'


def days_to_seconds(days: int) -> int:
    return days * 86400


def hours_to_seconds(hours: int) -> int:
    return hours * 3600


def minutes_to_seconds(minutes: int) -> int:
    return minutes * 60
