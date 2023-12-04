import datetime
import string
from inspect import isclass

from django.core.paginator import Paginator
from django.db.models import Q

import api.models
from api.models import *
from education.utils.request_service import get_request_ip_address
from education.utils.datetime_service import datetime_now
from web.utils.notices import get_notice_web


def get_models_classes():
    classes = []
    models_classes_name = [x for x in dir(api.models) if isclass(getattr(api.models, x))]

    for model_name in models_classes_name:
        instance = globals().get(model_name)
        meta = getattr(instance, '_meta', None)
        if meta:
            verbose_name_plural = getattr(meta, 'verbose_name_plural', None)
            if verbose_name_plural:
                classes.append(instance)

    classes = sorted(classes, key=lambda x: x._meta.verbose_name_plural)
    return classes


def get_model_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def get_first_model_or_none(model, **kwargs):
    try:
        obj = model.objects.filter(**kwargs)
        return obj[0] if obj else None

    except model.DoesNotExist:
        return None


def get_system() -> System | None:
    systems = System.objects.all()
    return systems[0] if systems else None


def get_or_create_ip_address(value: str) -> IPAddress:
    try:
        ip_address = IPAddress.objects.get(value=value)
    except IPAddress.DoesNotExist:
        ip_address = IPAddress.objects.create(value=value)
    return ip_address


def get_or_create_user_agent(value: str) -> UserAgent:
    try:
        user_agent = UserAgent.objects.get(value=value)
    except UserAgent.DoesNotExist:
        user_agent = UserAgent.objects.create(value=value)
    return user_agent


def get_or_create_request_method(name: str) -> RequestMethod:
    try:
        request_method = RequestMethod.objects.get(name=name)
    except RequestMethod.DoesNotExist:
        request_method = RequestMethod.objects.create(name=name)
    return request_method


def mark_ip_address_activity(request):
    ip_address = get_or_create_ip_address(get_request_ip_address(request))
    ip_address.last_minute_requests += 1
    ip_address.save()


def mark_user_activity(request):
    if not request.user.is_authenticated:
        return

    user_activity = UserActivity.objects.get(user_id=request.user.id)
    dt_now = datetime_now()

    user_activity.datetime_last_activity = dt_now

    if dt_now.date() != user_activity.date_last_online:
        if (dt_now.date() - user_activity.date_last_online).days == 1:
            user_activity.online_days_in_a_row += 1
        else:
            user_activity.online_days_in_a_row = 1

    user_activity.date_last_online = dt_now.date()

    user_activity.save()


def get_technical_work(is_now: bool = False) -> TechnicalWork | None:
    dt = datetime_now()
    filter_ = Q(datetime_end__gt=dt)
    if is_now:
        filter_ &= Q(datetime_begin__lte=dt)

    technical_work_list = TechnicalWork.objects.filter(filter_).order_by('datetime_end')
    return technical_work_list[0] if technical_work_list else technical_work_list


def get_blocked_ip_address(request) -> BlockedIPAddress | None:
    ip_address = get_model_or_none(IPAddress, value=get_request_ip_address(request))
    if ip_address:
        return get_model_or_none(BlockedIPAddress, ip_address_id=ip_address.id)


def get_blocked_user(request) -> BlockedUser | None:
    if not request.user.is_authenticated:
        return None
    return get_model_or_none(BlockedUser, user_id=request.user.id)


def block_ip_address(ip_address_id: int,
                     datetime_unlock: datetime.datetime = None,
                     cause: str = None
                     ) -> BlockedIPAddress:
    blocked_ip_address = get_model_or_none(BlockedIPAddress, ip_address_id=ip_address_id)
    if blocked_ip_address:

        if datetime_unlock:
            if datetime_unlock > blocked_ip_address.datetime_unlock:
                blocked_ip_address.datetime_unlock = datetime_unlock
            blocked_ip_address.cause = cause
            blocked_ip_address.save()

        return blocked_ip_address

    return BlockedIPAddress.objects.create(ip_address_id=ip_address_id,
                                           datetime_unlock=datetime_unlock,
                                           cause=cause)


def block_user(
        user_id: int,
        datetime_unlock: datetime.datetime = None,
        cause: str = None
) -> BlockedUser:
    blocked_user = get_model_or_none(BlockedUser, user_id=user_id)
    if blocked_user:

        if datetime_unlock:
            if datetime_unlock > blocked_user.datetime_unlock:
                blocked_user.datetime_unlock = datetime_unlock
            blocked_user.cause = cause
            blocked_user.save()

        return blocked_user

    return BlockedUser.objects.create(datetime_unlock=datetime_unlock, cause=cause)


def get_user_verification(request) -> UserVerification | None:
    if not request.user.is_authenticated:
        return None
    return get_model_or_none(UserVerification, user_id=request.user.id)


def if_student_verified(student_id: int) -> bool:
    return UserVerification.objects.exists(student_id=student_id)


class StudentRatingItem:
    def __init__(self, student: Student,
                 points: int = 0,
                 change_of_points: int = 0,
                 change_of_position: int = 0):
        self.student = student
        self.points = points
        self.change_of_points = change_of_points
        self.change_of_position = change_of_position


def get_student_rating_list(student_group_id: int = None,
                            date_begin: datetime.date = None,
                            date_end: datetime.date = None,
                            sort_by_points_change: bool = False,
                            ) -> list[StudentRatingItem]:
    if student_group_id:
        student_list = list(Student.objects.filter(group_id=student_group_id))
    else:
        student_list = list(Student.objects.all())

    # Удалим неверифицированных студентов из выборки.
    unverified_user_id_list = [x.user.id for x in UserVerification.objects.all()]
    i = 0
    while i < len(student_list):
        if student_list[i].user.id in unverified_user_id_list:
            student_list.pop(i)
            continue
        i += 1

    completing_task_list = CompletingTask.objects.filter(student__group_id=student_group_id)
    testing_result_list = TestResult.objects.filter(student__group_id=student_group_id)
    points_additional_list = PointsAdditional.objects.filter(student__group_id=student_group_id)

    data_total = []
    data_before = []
    data_after = []

    # Вычисление баллов до и после.
    for student in student_list:
        points_before = 0
        points_after = 0

        for item in completing_task_list:
            if item.student_id == student.id and item.points:
                el_date = item.assigned_task.datetime_create.date()

                if date_begin and el_date < date_begin:
                    points_before += item.points
                if date_end and el_date <= date_end:
                    points_after += item.points

        for item in testing_result_list:
            if item.student_id == student.id and item.points:
                el_date = item.assigned_test.date

                if date_begin and el_date < date_begin:
                    points_before += item.points
                if date_end and el_date <= date_end:
                    points_after += item.points

        for item in points_additional_list:
            if item.student_id == student.id and item.points:
                if date_begin and item.date_receiving < date_begin:
                    points_before += item.points
                if date_end and item.date_receiving <= date_end:
                    points_after += item.points

        data_total.append(StudentRatingItem(student=student, points=student.points,
                                            change_of_points=points_after - points_before))
        data_before.append(StudentRatingItem(student=student, points=points_before))
        data_after.append(StudentRatingItem(student=student, points=points_after))

    data_total = sorted(data_total, key=lambda x: x.points, reverse=True)
    data_before = sorted(data_before, key=lambda x: x.points, reverse=True)
    data_after = sorted(data_after, key=lambda x: x.points, reverse=True)

    # Получим изменение в позиции в списке.
    for student in student_list:
        i_total = 0
        for i in range(len(data_total)):
            if data_total[i].student.id == student.id:
                i_total = i
                break

        i_before = 0
        for i in range(len(data_before)):
            if data_before[i].student.id == student.id:
                i_before = i
                break

        i_after = 0
        for i in range(len(data_after)):
            if data_after[i].student.id == student.id:
                i_before = i
                break

        data_total[i_total].change_of_position = i_after - i_before

    if sort_by_points_change:
        return sorted(data_total, key=lambda x: x.change_of_points, reverse=True)
    else:
        return sorted(data_total, key=lambda x: x.points, reverse=True)


def get_hashtag_list(hashtag_list_id: int) -> list[Hashtag]:
    return [x.hashtag.name for x in HashtagFromList.objects.filter(hashtag_list_id=hashtag_list_id)]


def get_comment_list(obj) -> list[Comment]:
    if not obj.comment_list:
        return []
    return (Comment.objects
            .filter(comment_list_id=obj.comment_list.id)
            .order_by('-datetime_create'))


def clear_hashtags(text: str) -> str:
    words = text.split()
    for word in reversed(words):
        if len(word) > 1 and word[0] == '#':
            text = text.replace(f'#{word[1:]}', '', 1)
        else:
            break

    for word in words:
        word = word.translate(str.maketrans('', '', string.punctuation))
        if len(word) > 1 and word[0] == '#':
            text = text.replace(word, f'<p class="inline color-special">{word}</p>', 1)
        else:
            break

    text = text.strip()
    return text


def mark_notices_as_read(user_id: int, notice_id: int = None):
    if notice_id:
        notice = get_model_or_none(Notice, id=notice_id)
        if notice:
            notice.is_read = True
            notice.save()

    else:
        for notice in Notice.objects.filter(user_id=user_id, is_read=False):
            notice.is_read = True
            notice.save()


def get_notice_list(page: int = None,
                    user_id: int = None,
                    notice_code: NoticeCode = None) -> list[Notice]:
    filter_ = Q()
    if user_id:
        filter_ &= Q(user_id=user_id)
    if notice_code:
        filter_ &= Q(notice_type__code=notice_code.value)

    notices_raw = (Notice.objects.filter(filter_)
                   .order_by('is_read', '-datetime_create'))

    notices = [get_notice_web(notice) for notice in notices_raw]
    paginator = Paginator(notices, PAGE_LIMIT_DEFAULT)

    return paginator.get_page(page)


def get_post_list(student_group_id: int = None, user_id: int = None) -> list[dict]:
    if student_group_id:
        posts_raw = (PostForStudentGroup.objects
                     .filter(post__is_published=True, student_group_id=student_group_id)
                     .order_by('-post__datetime_create'))
        posts_raw = [x.post for x in posts_raw]
    else:
        posts_raw = (Post.objects.filter(is_published=True).order_by('-datetime_create'))

    posts = []
    for post in posts_raw:
        item = {
            'id': post.id,
            'header': post.header,
            'text': post.text,
            'description': post.description,
            'datetime_create': post.datetime_create,
            'count_views': post.count_views,
            'viewed': True,
        }
        if user_id:
            posts_view_id = [x.id for x in PostView.objects.filter(user_id=user_id)] if user_id else []
            item['viewed'] = post.id in posts_view_id

        if post.hashtag_list:
            item['hashtags'] = get_hashtag_list(post.hashtag_list.id)

        posts.append(item)

    return posts


def get_event_list(student_group_id: int = None,
                   is_current: bool = False) -> list[dict]:
    events = []
    if student_group_id:
        assigned_events_raw = AssignedEvent.objects.filter(student_group_id=student_group_id)
        assigned_events = []

        if is_current:
            dt_now = datetime_now()
            for assigned_event in assigned_events_raw:
                if assigned_event.datetime_end:
                    if assigned_event.datetime_end > dt_now:
                        assigned_events.append(assigned_event)
                elif assigned_event.event.datetime_end > dt_now:
                    assigned_events.append(assigned_event)

            assigned_events = sorted(assigned_events,
                                     key=lambda x: x.datetime_begin if x.datetime_begin else x.event.datetime_begin,
                                     reverse=True)
            assigned_events = sorted(assigned_events,
                                     key=lambda x: x.datetime_end if x.datetime_end else x.event.datetime_end,
                                     reverse=True)
        else:
            assigned_events = assigned_events_raw

        for assigned_event in assigned_events:
            events.append({
                'id': assigned_event.event.id,
                'datetime_begin': (assigned_event.datetime_begin if assigned_event.datetime_begin
                                   else assigned_event.event.datetime_begin),
                'datetime_end': (assigned_event.datetime_end if assigned_event.datetime_end
                                 else assigned_event.event.datetime_end),
                'image_url': assigned_event.event.image.url if assigned_event.event.image else None,
                'name': assigned_event.event.name,
            })

    else:
        filter_ = Q()
        if is_current:
            filter_ &= Q(datetime_end__gt=datetime_now())

        for event in Event.objects.filter(filter_).order_by('datetime_end', 'datetime_begin'):
            events.append({
                'id': event.id,
                'datetime_begin': event.datetime_begin,
                'datetime_end': event.datetime_end,
                'image_url': event.image.url if event.image else None,
                'name': event.name,
            })

    return events


def get_test_list(student_group_id: int = None,
                  student_id: int = None,
                  is_current: bool = False) -> list[dict]:
    tests = []

    if student_group_id:
        assigned_test_list = AssignedTest.objects.filter(student_group_id=student_group_id).order_by('date')
        test_result_list = TestResult.objects.filter(student_id=student_id) if student_id else []

        for assigned_test in assigned_test_list:
            item = {
                'date': assigned_test.date,
                'is_open': assigned_test.is_open,
                'open_results': assigned_test.open_results,
                'image_url': assigned_test.test.image.url if assigned_test.test.image else None,
                'name': assigned_test.test.name,
                'section_name': assigned_test.test.course_section.name
            }
            passed = False
            for tests_result in test_result_list:
                if tests_result.assigned_test_id == assigned_test.id:
                    item['points'] = tests_result.points
                    item['points_max'] = assigned_test.test.points
                    passed = True
                    break
            if is_current and passed:
                continue

            tests.append(item)

    else:
        for test in Test.objects.all().order_by('-datetime_create'):
            tests.append({
                'image_url': test.image.url if test.image else None,
                'name': test.name,
                'section_name': test.course_section.name
            })

    return tests


def get_task_list_by_sections(student_group_id: int = None,
                              student_id: int = None,
                              is_current: bool = False,
                              empty_sections: bool = False) -> list[dict]:
    sections_raw = CourseSection.objects.all().order_by('position')
    sections = [{'id': x.id, 'name': x.name, 'tasks': []} for x in sections_raw]

    if student_group_id:
        filter_ = Q(student_group_id=student_group_id)
        if is_current:
            filter_ &= Q(deadline__gt=datetime_now())

        assigned_task_list = (AssignedTask.objects
                              .filter(filter_)
                              .order_by('-deadline', '-readline'))

        if student_id:
            completing_task_list = CompletingTask.objects.filter(student_id=student_id)
        else:
            completing_task_list = []

        for assigned_task in assigned_task_list:
            for i, section in enumerate(sections):
                if assigned_task.task.course_section.id == section['id']:

                    image_url = assigned_task.task.image.url if assigned_task.task.image else None
                    if not image_url and assigned_task.task.course_section.image:
                        image_url = assigned_task.task.course_section.image.url

                    item = {
                        'id': assigned_task.task.id,
                        'readline': assigned_task.readline,
                        'deadline': assigned_task.deadline,
                        'image_url': image_url,
                        'name': assigned_task.task.name,
                        'difficulty_code': assigned_task.task.difficulty.code if assigned_task.task.difficulty else None,
                        'viewed': False if student_id else True,
                    }
                    for tasks_complete in completing_task_list:
                        if tasks_complete.assigned_task_id == assigned_task.id:
                            item['status_code'] = tasks_complete.status.code
                            item['points'] = tasks_complete.points
                            item['points_max'] = assigned_task.task.points
                            item['viewed'] = True
                            break

                    sections[i]['tasks'].append(item)
                    break

    else:
        for task in Task.objects.all().order_by('-datetime_create'):
            for i, section in enumerate(sections):
                if task.course_section.id == section['id']:

                    image_url = task.image.url if task.image else None
                    if not image_url and task.course_section.image:
                        image_url = task.course_section.image.url

                    sections[i]['tasks'].append({
                        'id': task.id,
                        'image_url': image_url,
                        'name': task.name,
                        'difficulty_code': task.difficulty.code if task.difficulty else None,
                        'viewed': True,
                    })
                    break

    if not empty_sections:
        i = 0
        while i < len(sections):
            if not sections[i]['tasks']:
                sections.pop(i)
                continue
            i += 1

    return sections


def get_achievement_list(student_id: int = None, is_private: bool = None) -> list[dict]:
    levels_raw = AchievementLevel.objects.all().order_by('achievement_id', 'level')

    filter_ = Q()
    if is_private is not None:
        filter_ &= Q(is_private=is_private)
    achievements_raw = Achievement.objects.filter(filter_)

    student_achievements_raw = (StudentAchievement.objects
                                .filter(student_id=student_id)
                                if student_id else None)
    achievements = []

    for achievement in achievements_raw:
        levels = []
        student_achievement_level = None
        is_new = False

        for sa in student_achievements_raw or []:
            if sa.achievement_id == achievement.id:
                student_achievement_level = sa.level
                if not sa.viewed:
                    is_new = True

        for level in filter(lambda x: x.achievement_id == achievement.id, levels_raw):
            levels.append({
                'id': level.id,
                'name': level.name,
                'description': level.description,
                'level': level.level,
                'required_value': level.required_value,
                'badge_awarded': level.badge_awarded,
                'rank_code': level.rank.code,
                'received': bool(student_achievement_level and student_achievement_level >= level.level),
            })

        if levels:
            achievements.append({
                'id': achievement.id,
                'icon_name': achievement.icon_name,
                'name': achievement.name,
                'description': achievement.description,
                'is_private': achievement.is_private,
                'is_systemic': achievement.is_systemic,

                'rank_code': levels[-1]['rank_code'],
                'is_new': is_new,
                'received': levels[-1]['received'],
                'levels': levels,
            })

    achievements = sorted(achievements, key=lambda x: len(x['levels']))
    achievements = sorted(achievements, key=lambda x: x['rank_code'])
    achievements = sorted(achievements, key=lambda x: x['received'], reverse=True)
    achievements = sorted(achievements, key=lambda x: x['is_new'], reverse=True)

    return achievements


def get_student_achievement_list(student_id: int) -> list[dict]:
    levels_raw = AchievementLevel.objects.all().order_by('achievement_id', 'level')
    student_achievements_raw = StudentAchievement.objects.filter(student_id=student_id)
    achievements = []

    for student_achievement in student_achievements_raw:
        achievement = student_achievement.achievement
        levels = list(filter(lambda x: (x.achievement_id == achievement.id and
                                        x.level == student_achievement.level),
                             levels_raw))

        if levels:
            level: AchievementLevel = levels[0]
            achievements.append({
                'icon_name': level.achievement.icon_name,
                'name': level.name or (level.achievement.name + ' ' + f'{level.level} ур.'),
                'description': level.description,
                'rank_code': level.rank.code,
                'is_private': level.achievement.is_private,
            })

    return sorted(achievements, key=lambda x: x['rank_code'], reverse=True)


def get_user(user: User) -> dict:
    personal_info = PersonalInformation.objects.get(user_id=user.id)
    user_activity = UserActivity.objects.get(user_id=user.id)
    student = get_model_or_none(Student, user_id=user.id)

    user_ = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'datetime_last_activity': user_activity.datetime_last_activity,
        'is_admin': user.is_superuser,
        'is_teacher': bool(get_model_or_none(Teacher, user_id=user.id)),

        'days': (datetime_now().date() - user.date_joined.date()).days + 1,
        'online_days_in_a_row': user_activity.online_days_in_a_row,
        'online_days_in_a_row_max': user_activity.online_days_in_a_row_max,
        'count_requests': Log.objects.filter(user_id=user.id).count(),
    }

    if personal_info.image:
        user_['image_url'] = personal_info.image.url
    if personal_info.cover_image:
        user_['cover_image_url'] = personal_info.cover_image.url
    if personal_info.about_me:
        user_['about_me'] = personal_info.about_me

    if student:
        levels = list(Level.objects.all().order_by('value'))
        prev_points = list(filter(lambda x: x.value == student.level.value, levels))[0].points
        if student.level.value == levels[-1].value:
            next_points = None
        else:
            next_points = list(filter(lambda x: x.value == student.level.value + 1, levels))[0].points
        points_to_next_level = next_points - student.points

        students = Student.objects.filter(group_id=student.group.id).order_by('-points')
        rating_position = 0
        for i in range(len(students)):
            if student.points >= students[i].points:
                rating_position = i + 1
                break

        student_activity = StudentActivity.objects.get(student_id=student.id)
        student_ = {
            'rank_code': student.rank.code,
            'coins': student.coins,
            'rating_position': rating_position,
            'group': {
                'name': student.group.name,
            },
            'level': {
                'value': student.level.value,
                'points': student.points,
                'prev_points': prev_points,
                'next_points': next_points,
                'points_to_next_level': points_to_next_level,
                'percent': (100 - round(points_to_next_level / (next_points - prev_points) * 100)
                            if next_points else 100),
            },
            'pass_tasks_first_time_in_a_row': student_activity.pass_tasks_first_time_in_a_row,
            'pass_tasks_first_time_in_a_row_max': student_activity.pass_tasks_first_time_in_a_row_max,
        }
        if student.option:
            student_['option'] = student.option

        project = Project.objects.get(student_id=student.id)
        project_ = {
            'id': project.id,
            'name': project.name,
            'status_code': project.status.code,
            'urls': {
                'document': project.document_url,
                'figma': project.figma_url,
                'drawio': project.drawio_url,
                'github': project.github_url,
            },
        }
        student_['project'] = project_

        student_['achievements'] = get_student_achievement_list(student_id=student.id)

        tasks_complete = CompletingTask.objects.filter(student_id=student.id)
        student_['count_tasks_complete'] = tasks_complete.count()
        student_['points_for_tasks'] = sum([x.points for x in tasks_complete])
        student_['average_count_attempts_for_tasks'] = (round(sum([x.total_attempts for x in tasks_complete]) /
                                                              len(tasks_complete), 2)
                                                        if tasks_complete else 0)

        tests_result = TestResult.objects.filter(student_id=student.id)
        student_['best_test_result'] = (max([round((x.points - x.penalty_points) / x.assigned_test.test.points * 100)
                                             for x in tests_result])
                                        if tests_result else 0)
        student_['points_for_tests'] = sum([x.points for x in tests_result])

        student_['additional_points'] = sum([x.points for x in PointsAdditional.objects.filter(student_id=student.id)])

        user_['student'] = student_

    return user_


def get_project(project: Project, comments_page: int = None) -> dict:
    comments = get_comment_list(project)
    if comments:
        comments_paginator = Paginator(comments, PAGE_LIMIT_DEFAULT)
        comments = comments_paginator.get_page(comments_page)

    return {
        'id': project.id,
        'name': project.name,
        'urls': {
            'document': project.document_url,
            'figma': project.figma_url,
            'drawio': project.drawio_url,
            'github': project.github_url,
        },
        'status_code': project.status.code,
        'comments': comments,
        'comments_page': comments_page,
    }


def get_post(post: Post, comments_page: int = None) -> dict:
    comments = get_comment_list(post)
    if comments:
        comments_paginator = Paginator(comments, PAGE_LIMIT_DEFAULT)
        comments = comments_paginator.get_page(comments_page)

    return {
        'id': post.id,
        'header': post.header,
        'description': post.description,
        'text': clear_hashtags(post.text),
        'datetime_create': post.datetime_create,
        'count_views': post.count_views,
        'hashtags': get_hashtag_list(post.hashtag_list.id) if post.hashtag_list else [],
        'comments': comments,
        'comments_page': comments_page,
    }


def get_event(event: Event,
              assigned_event: AssignedEvent = None,
              comments_page: int = None) -> dict:
    comments = get_comment_list(event)
    if comments:
        comments_paginator = Paginator(comments, PAGE_LIMIT_DEFAULT)
        comments = comments_paginator.get_page(comments_page)

    event_ = {
        'datetime_begin': event.datetime_begin,
        'datetime_end': event.datetime_end,
        'name': event.name,
        'image_url': event.image.url if event.image else None,
        'text': clear_hashtags(event.text),
        'points': event.points,
        'comments': comments,
        'comments_page': comments_page,
    }
    if assigned_event:
        if assigned_event.datetime_begin:
            event_['datetime_begin'] = assigned_event.datetime_begin
        if assigned_event.datetime_end:
            event_['datetime_end'] = assigned_event.datetime_end

    return event_


def get_test(test: Test,
             assigned_test: AssignedTest = None,
             comments_page: int = None) -> dict:
    comments = get_comment_list(test)
    if comments:
        comments_paginator = Paginator(comments, PAGE_LIMIT_DEFAULT)
        comments = comments_paginator.get_page(comments_page)

    test_ = {
        'image_url': test.image.url if test.image else None,
        'name': test.name,
        'text': clear_hashtags(test.text),
        'points': test.points,
        'time': test.time,
        'shuffle_order_tasks': test.shuffle_order_tasks,
        'shuffle_order_answers': test.shuffle_order_answers,
        'enable_points': test.enable_points,
        'section_name': test.course_section.name,
        'comments': comments,
        'comments_page': comments_page,
    }
    if assigned_test:
        test_['date'] = assigned_test.date
        test_['is_open'] = assigned_test.is_open
        test_['open_results'] = assigned_test.open_results

    return test_


def get_events_assigned_by_groups(event_id: int) -> list[dict]:
    items = []
    assigned_event_list = AssignedEvent.objects.filter(event_id=event_id)

    for assigned_event in assigned_event_list:
        item = {
            'id': assigned_event.student_group.id,
            'name': assigned_event.student_group.name,
        }
        if assigned_event.datetime_begin:
            item['datetime_begin'] = assigned_event.datetime_begin
        if assigned_event.datetime_end:
            item['datetime_end'] = assigned_event.datetime_end

        items.append(item)

    return items


def get_task(task: Task,
             assigned_task: AssignedTask = None,
             completing_task: CompletingTask = None,
             comments_page: int = None,
             private_comments_page: int = None) -> dict:
    task_ = {
        'id': task.id,
        'name': task.name,
        'text': clear_hashtags(task.text),
        'points': task.points,
        'max_attempts': task.max_attempts,
        'attempts_per_day': task.attempts_per_day,
        'count_forms': task.count_forms,
        'variable_count_forms': task.variable_count_forms,
        'manual_check_result': task.manual_check_result,
        'section_name': task.course_section.name,
        'difficulty_code': task.difficulty.code if task.difficulty else None,
        'answer_format_code': task.answer_format.code,
    }

    if task.image:
        task_['image_url'] = task.image.url
    elif task.course_section.image:
        task_['image_url'] = task.course_section.image.url

    if task.hashtag_list:
        task_['hashtags'] = get_hashtag_list(task.hashtag_list.id)

    checking_access_list = CheckingTaskAccess.objects.filter(task_id=task.id)
    if checking_access_list:
        items = []
        for item in checking_access_list:
            items.append({
                'icon_name': item.script.icon_name,
                'description': item.script.description,
            })
        task_['checks_access'] = items

    checking_complete_list = CheckingCompletingTask.objects.filter(task_id=task.id)
    if checking_complete_list:
        items = []
        for item in checking_complete_list:
            items.append({
                'icon_name': item.script.icon_name,
                'description': item.script.description,
            })
        task_['checks_complete'] = items

    comments = get_comment_list(task)
    if comments:
        comments_paginator = Paginator(comments, PAGE_LIMIT_DEFAULT)
        task_['comments'] = comments_paginator.get_page(comments_page)
        task_['comments_page'] = comments_page

    if assigned_task:
        task_['readline'] = assigned_task.readline
        task_['deadline'] = assigned_task.deadline

        if completing_task:
            task_['complete'] = {
                'datetime_sent': completing_task.datetime_sent,
                'total_attempts': completing_task.total_attempts,
                'attempts_today': completing_task.attempts_today,
                'kwargs': completing_task.kwargs,
                'points': completing_task.points,
                'status_code': completing_task.status.code,
            }

            comments = get_comment_list(completing_task)
            if comments:
                comments_paginator = Paginator(comments, PAGE_LIMIT_DEFAULT)
                task_['private_comments'] = comments_paginator.get_page(private_comments_page)
                task_['private_comments_page'] = private_comments_page

    return task_
