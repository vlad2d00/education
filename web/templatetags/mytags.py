import copy

from django import template

from api.db.config import ProjectStatusCode, NoticeCode, RankCode, TaskStatusCode, DifficultyCode, \
    IMAGE_TEMPLATE_FORMAT, AnswerFormatCode
from api.db.dao import get_model_or_none, get_technical_work, get_system as dao_get_system
from api.models import Notice, ProjectStatus, Rank, Feedback, PostView, PostForStudentGroup, Student, TaskStatus, \
    Difficulty, StudentAchievement, Teacher, Post, PersonalInformation
from api.utils.strings_storage import StringStorage
from education.utils.datetime_service import datetime_now, datetime_to_string_relative, datetime_timezone, \
    datetime_timezone_now
from web.utils.navigation import NAVIGATION_ITEMS, NavigationItemId

register = template.Library()


@register.filter
def create_range(value, start_index=0):
    return range(start_index, value + start_index)


@register.simple_tag()
def datetime(dt=None,
             show_day_week: bool = False,
             show_words: bool = True,
             fixed_time: bool = False,
             fixed_date: bool = True):
    if not dt:
        dt = datetime_now()
    return datetime_to_string_relative(dt_target=datetime_timezone(dt),
                                       dt_original=datetime_timezone_now(),
                                       show_day_week=show_day_week,
                                       show_words=show_words,
                                       fixed_time=fixed_time,
                                       fixed_date=fixed_date)


@register.simple_tag()
def get_datetime_now():
    return datetime_now()


@register.simple_tag()
def get_name(name: str, id: int = None):
    return name + ('_' + str(id) if id else '')


@register.simple_tag()
def get_item(obj, index: int):
    return obj[index] if obj else None


@register.simple_tag()
def get_system():
    dao_get_system()


@register.simple_tag()
def get_rank_code_list():
    return {x.name: x.value for x in RankCode}


@register.simple_tag()
def get_rank_name(code: int):
    return Rank.objects.get(code=code).name


@register.simple_tag()
def get_rank_css_class(code: int):
    ranks_name = {x.value: x.name for x in RankCode}
    return 'color-' + ranks_name[code].lower()


@register.simple_tag()
def get_project_status_code_list():
    return {x.name: x.value for x in ProjectStatusCode}


@register.simple_tag()
def get_project_status_name(code: int):
    return ProjectStatus.objects.get(code=code).name


@register.simple_tag()
def get_project_status_css_class(code: int):
    if code == ProjectStatusCode.RETURNED.value:
        color = 'error'
    elif code == ProjectStatusCode.APPROVAL.value:
        color = 'warning'
    elif code == ProjectStatusCode.COMPLETED.value:
        color = 'success'
    else:
        color = 'secondary'

    return 'color-' + color


@register.simple_tag()
def get_task_status_code_list():
    return {x.name: x.value for x in TaskStatusCode}


@register.simple_tag()
def get_task_status_name(code: int):
    return TaskStatus.objects.get(code=code).name


@register.simple_tag()
def get_task_status_css_class(code: int):
    if code in (TaskStatusCode.UNDERGOING_TESTING.value, TaskStatusCode.REVIEW.value):
        color = 'warning'
    elif code in (TaskStatusCode.TESTS_FAILED.value, TaskStatusCode.RETURNED.value):
        color = 'error'
    elif code in (TaskStatusCode.TESTS_PASSED.value, TaskStatusCode.DONE.value):
        color = 'success'
    else:
        color = 'secondary'

    return 'message-' + color


@register.simple_tag()
def get_difficulty_code_list():
    return {x.name: x.value for x in DifficultyCode}


@register.simple_tag()
def get_difficulty_name(code: int):
    return Difficulty.objects.get(code=code).name


@register.simple_tag()
def get_achievement_bg_css_class(code: int):
    for i in RankCode:
        if i.value == code:
            return 'achievement-bg-' + i.name.lower()

    return ''


@register.simple_tag()
def get_answer_format_code_list():
    return {x.name: x.value for x in AnswerFormatCode}


@register.simple_tag()
def get_notice_code_list():
    return {x.name: x.value for x in NoticeCode}


@register.simple_tag()
def get_header():
    return StringStorage.HEADER.value


@register.simple_tag()
def get_count_notice(request):
    return len(Notice.objects.filter(user_id=request.user.id, is_read=False))


@register.inclusion_tag('web/components/user-image.html')
def user_image(request):
    personal_information = PersonalInformation.objects.get(user_id=request.user.id)
    return {
        'request': request,
        'user': {
            'image_url': personal_information.image.url if personal_information.image else None
        }
    }


@register.inclusion_tag('web/components/navigation.html')
def navigation(request):
    if not request.user.is_authenticated:
        return {}

    items = []
    for item in NAVIGATION_ITEMS:
        items.append(copy.copy(item))

    student = get_model_or_none(Student, user_id=request.user.id)
    teacher = get_model_or_none(Teacher, user_id=request.user.id)

    def _set_count_notice(id: NavigationItemId, count: int):
        for item in items:
            if item.id == id.value:
                item.count_notice = count

    if request.user.is_staff:
        _set_count_notice(id=NavigationItemId.FEEDBACK,
                          count=Feedback.objects.filter(is_read=False).count())

    posts_all = None
    if request.user.is_staff or teacher:
        posts_all = Post.objects.filter(is_published=True).count()
    elif student:
        posts_all = PostForStudentGroup.objects.filter(post__is_published=True,
                                                       student_group_id=student.group.id).count()

    if posts_all:
        posts_viewed = PostView.objects.filter(user_id=request.user.id).count()
        _set_count_notice(id=NavigationItemId.HOME,
                          count=posts_all - posts_viewed)

    if student:
        count_achievements = StudentAchievement.objects.filter(student_id=student.id,
                                                               viewed=False).count()
        _set_count_notice(id=NavigationItemId.ACHIEVEMENTS,
                          count=count_achievements)

    return {
        'request': request,
        'navigation': items,
        'username': request.user.username,
    }


@register.inclusion_tag('web/components/technical-work.html')
def technical_work():
    return {
        'technical_work': get_technical_work(is_now=False),
    }


@register.inclusion_tag('web/components/pagination.html')
def pagination(items, page: int, url_name: str):
    return {
        'items': items,
        'page': page,
        'url_name': url_name,
    }


@register.inclusion_tag('web/components/hashtags.html')
def hashtags(items: list[str]):
    return {
        'items': items,
    }


@register.inclusion_tag('web/components/post-footer.html')
def post_footer(hashtag_list, count_views: int, datetime_create):
    return {
        'hashtag_list': hashtag_list,
        'count_views': count_views,
        'datetime_create': datetime_create,
    }


@register.inclusion_tag('web/components/event-item.html')
def event_item(event):
    return {
        'event': event,
    }


@register.inclusion_tag('web/components/task-item.html')
def task_item(task):
    return {
        'task': task,
    }


def get_admin_action_params(request,
                            model_name: str,
                            action_name: str,
                            obj_id: int = None,
                            is_absolute: bool = False):
    model_name = model_name.lower()
    app_label = 'auth' if model_name == 'user' else 'api'
    return {
        'request': request,
        'url_name': f'admin:{app_label}_{model_name}_{action_name}',
        'action_name': action_name,
        'obj_id': obj_id,
        'is_absolute': is_absolute,
    }


@register.inclusion_tag('web/components/achievement-item.html')
def achievement_item(request,
                     name: str,
                     description: str,
                     rank_code: int,
                     is_private: bool = False):
    return {
        'request': request,
        'name': name,
        'description': description,
        'rank_code': rank_code,
        'is_private': is_private,
    }


@register.inclusion_tag('web/components/admin-action.html')
def admin_action_add(request,
                     model_name: str,
                     is_absolute: bool = False):
    return get_admin_action_params(request,
                                   model_name=model_name,
                                   action_name='add',
                                   is_absolute=is_absolute)


@register.inclusion_tag('web/components/admin-action.html')
def admin_action_change(request,
                        model_name: str,
                        obj_id: int,
                        is_absolute: bool = False):
    return get_admin_action_params(request,
                                   model_name=model_name,
                                   action_name='change',
                                   obj_id=obj_id,
                                   is_absolute=is_absolute)


@register.inclusion_tag('web/components/action.html')
def custom_action(image_path: str,
                  url_name: str,
                  image_name: str,
                  param=None,
                  is_absolute: bool = False):
    return {
        'image_path': image_path,
        'url_name': url_name,
        'image_url': IMAGE_TEMPLATE_FORMAT.format(image_name),
        'param': param,
        'is_absolute': is_absolute,
    }


@register.inclusion_tag('web/components/include.html')
def svg(image_name: str):
    return {
        'template_name': IMAGE_TEMPLATE_FORMAT.format(image_name)
    }
