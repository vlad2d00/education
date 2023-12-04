import json

from api.models import *


class NoticeWeb:
    def __init__(self,
                 image_name: str,
                 image_url: str = None,
                 kwargs: dict = None):
        self.image_name = image_name
        self.image_url = image_url
        self.kwargs = kwargs


def notice_added_user_for_verification(kwargs: dict):
    user = User.objects.get(id=kwargs['user_id'])
    return NoticeWeb(image_name='user',
                     kwargs={
                         'username': user.username,
                         'user_full_name': user.first_name + ' ' + user.last_name,
                     })


def notice_feedback_left(kwargs: dict):
    feedback = Feedback.objects.get(id=kwargs['feedback_id'])
    return NoticeWeb(image_name='comment',
                     kwargs={
                         'student_group_name': feedback.student_group.name if feedback.student_group else None,
                         'feedback_text': feedback.text,
                     })


def notice_need_issue_badge_for_achievement(kwargs: dict):
    student_achievement = StudentAchievement.objects.get(id=kwargs['student_achievement_id'])
    return NoticeWeb(image_name='trophy',
                     kwargs={
                         'username': student_achievement.student.user.username,
                         'user_full_name': (student_achievement.student.user.first_name + ' ' +
                                            student_achievement.student.user.last_name),
                         'achievement_name': student_achievement.achievement.name,

                         'achievement_level': student_achievement.level,
                         'achievement_rank_code': AchievementLevel.objects.filter(
                             achievement_id=student_achievement.achievement,
                             level=student_achievement.level)[0].rank.code,
                     })


def notice_update_project_name(kwargs: dict):
    project = Project.objects.get(id=kwargs['project_id'])
    return NoticeWeb(image_name='project',
                     kwargs={
                         'username': project.student.user.username,
                         'user_full_name': project.student.user.first_name + ' ' + project.student.user.last_name,
                         'project_name': kwargs['project_name'],
                     })


def notice_task_comment_left(kwargs: dict):
    comment = Comment.objects.get(id=kwargs['comment_id'])
    task = Task.objects.get(id=kwargs['task_id'])
    return NoticeWeb(image_name='comment',
                     kwargs={
                         'username': comment.user.username,
                         'user_full_name': comment.user.first_name + ' ' + comment.user.last_name,
                         'task_id': task.id,
                         'task_name': task.name,
                     })


def notice_test_comment_left(kwargs: dict):
    comment = Comment.objects.get(id=kwargs['comment_id'])
    test = Test.objects.get(id=kwargs['test_id'])
    return NoticeWeb(image_name='comment',
                     kwargs={
                         'username': comment.user.username,
                         'user_full_name': comment.user.first_name + ' ' + comment.user.last_name,
                         'test_id': test.id,
                         'test_name': test.name,
                     })


def notice_user_verified(kwargs: dict):
    return NoticeWeb(image_name='check')


def notice_happy_birthday(kwargs: dict):
    return NoticeWeb(image_name='cake')


def notice_new_level(kwargs: dict):
    return NoticeWeb(image_name='up',
                     kwargs={
                         'level': kwargs['level'],
                     })


def notice_update_project_status(kwargs: dict):
    project = Project.objects.get(id=kwargs['project_id'])
    project_status = ProjectStatus.objects.get(code=kwargs['status_code'])
    return NoticeWeb(image_name='project',
                     kwargs={
                         'project_id': project.id,
                         'project_status_code': project_status.code,
                     })


def notice_achievement_received(kwargs: dict):
    achievement = Achievement.objects.get(id=kwargs['achievement_id'])
    achievement_level = AchievementLevel.objects.get(achievement_id=achievement.id,
                                                     level=kwargs['achievement_level'])
    kwargs = {
        'achievement_name': achievement_level.name or achievement.name,
        'achievement_rank_code': achievement_level.rank.code,
    }
    if AchievementLevel.objects.filter(achievement_id=achievement.id).count() > 1:
        kwargs['achievement_level'] = achievement_level.level

    return NoticeWeb(image_name='trophy',
                     kwargs=kwargs)


def notice_update_rank(kwargs: dict):
    rank = Rank.objects.get(id=kwargs['rank_id'])
    return NoticeWeb(image_name='star',
                     kwargs={
                         'rank_name': rank.name,
                     })


def notice_update_completing_task_status(kwargs: dict):
    task = Task.objects.get(id=kwargs['task_id'])
    task_status = TaskStatus.objects.get(code=kwargs['status_code'])
    return NoticeWeb(image_name='task',
                     kwargs={
                         'task_id': task.id,
                         'task_name': task.name,
                         'task_status_code': task_status.code,
                     })


def notice_additional_points_received(kwargs: dict):
    points_additional = PointsAdditional.objects.get(id=kwargs['points_additional_id'])
    return NoticeWeb(image_name='task',
                     kwargs={
                         'points': points_additional.points,
                         'comment': points_additional.comment,
                     })


def notice_project_comment_left(kwargs: dict):
    comment = Comment.objects.get(id=kwargs['comment_id'])
    return NoticeWeb(image_name='comment',
                     kwargs={
                         'username': comment.user.username,
                         'user_full_name': comment.user.first_name + ' ' + comment.user.last_name,
                     })


def notice_completing_task_comment_left(kwargs: dict):
    comment = Comment.objects.get(id=kwargs['comment_id'])
    task = Task.objects.get(id=kwargs['task_id'])
    return NoticeWeb(image_name='comment',
                     kwargs={
                         'username': comment.user.username,
                         'user_full_name': comment.user.first_name + ' ' + comment.user.last_name,
                         'task_id': task.id,
                         'task_name': task.name,
                     })


def notice_post_added(kwargs: dict):
    post = Post.objects.get(id=kwargs['post_id'])
    return NoticeWeb(image_name='file-lines',
                     kwargs={
                         'post_id': post.id,
                         'post_header': post.header,
                     })


def notice_assigned_task(kwargs: dict):
    task = Task.objects.get(id=kwargs['task_id'])
    return NoticeWeb(image_name='task',
                     kwargs={
                         'task_id': task.id,
                         'task_name': task.name,
                         'task_section_name': task.course_section.name,
                     })


def notice_assigned_event(kwargs: dict):
    event = Event.objects.get(id=kwargs['event_id'])
    return NoticeWeb(image_name='calendar',
                     kwargs={
                         'event_id': event.id,
                         'event_name': event.name,
                     })


def notice_assigned_test(kwargs: dict):
    test = Test.objects.get(id=kwargs['test_id'])
    return NoticeWeb(image_name='ballot-check',
                     kwargs={
                         'test_id': test.id,
                         'test_name': test.name,
                     })


def notice_update_test_open_status(kwargs: dict):
    test = Test.objects.get(id=kwargs['test_id'])
    return NoticeWeb(image_name='ballot-check',
                     kwargs={
                         'test_id': test.id,
                         'test_name': test.name,
                         'test_is_open': kwargs['is_open'],
                     })


def notice_update_test_results_status(kwargs: dict):
    test = Test.objects.get(id=kwargs['test_id'])
    return NoticeWeb(image_name='ballot-check',
                     kwargs={
                         'test_id': test.id,
                         'test_name': test.name,
                         'test_open_results': kwargs['open_results'],
                     })


def notice_(kwargs: dict):
    return NoticeWeb(image_name='',
                     kwargs={
                     })


NOTICE_FUNC_WEB_LIST = {
    # Для персонала и преподавателей:
    NoticeCode.ADDED_USER_FOR_VERIFICATION: notice_added_user_for_verification,
    NoticeCode.FEEDBACK_LEFT: notice_feedback_left,
    NoticeCode.NEED_ISSUE_BADGE_FOR_ACHIEVEMENT: notice_need_issue_badge_for_achievement,
    NoticeCode.UPDATE_PROJECT_NAME: notice_update_project_name,
    NoticeCode.TASK_COMMENT_LEFT: notice_task_comment_left,
    NoticeCode.TEST_COMMENT_LEFT: notice_test_comment_left,

    # Для студентов личные:
    NoticeCode.USER_VERIFIED: notice_user_verified,
    NoticeCode.HAPPY_BIRTHDAY: notice_happy_birthday,
    NoticeCode.NEW_LEVEL: notice_new_level,
    NoticeCode.UPDATE_PROJECT_STATUS: notice_update_project_status,
    NoticeCode.ACHIEVEMENT_RECEIVED: notice_achievement_received,
    NoticeCode.UPDATE_RANK: notice_update_rank,
    NoticeCode.UPDATE_COMPLETING_TASK_STATUS: notice_update_completing_task_status,
    NoticeCode.ADDITIONAL_POINTS_RECEIVED: notice_additional_points_received,
    NoticeCode.PROJECT_COMMENT_LEFT: notice_project_comment_left,
    NoticeCode.COMPLETING_TASK_COMMENT_LEFT: notice_completing_task_comment_left,

    # Для студентов групповые:
    NoticeCode.POST_ADDED: notice_post_added,
    NoticeCode.ASSIGNED_TASK: notice_assigned_task,
    NoticeCode.ASSIGNED_EVENT: notice_assigned_event,
    NoticeCode.ASSIGNED_TEST: notice_assigned_test,
    NoticeCode.UPDATE_TEST_OPEN_STATUS: notice_update_test_open_status,
    NoticeCode.UPDATE_TEST_RESULTS_STATUS: notice_update_test_results_status,
}


def get_notice_web(notice: Notice):
    notice_codes = {x.value: x for x in NoticeCode}
    notice_code = notice_codes[notice.notice_type.code]
    func = NOTICE_FUNC_WEB_LIST[notice_code]
    kwargs = json.loads(notice.kwargs or {})

    notice_web: NoticeWeb = func(kwargs)

    response = {
        'id': notice.id,
        'datetime_create': notice.datetime_create,
        'code': notice.notice_type.code,
        'is_read': notice.is_read,
        'image_name': IMAGE_TEMPLATE_FORMAT.format(notice_web.image_name),
        'image_url': notice_web.image_url,
    }
    for key in notice_web.kwargs or []:
        response[key] = notice_web.kwargs[key]

    return response
