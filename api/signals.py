import datetime
import json
from functools import wraps

from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver

from api.db.dao import get_model_or_none
from api.models import *
from api.utils.strings_storage import StringStorage
from api.utils.completing_task_checks import CHECKING_COMPLETING_TASK_FUNC_BY_NAME
from education.middleware.logged_in_user import LoggedInUser
from education.utils.datetime_service import datetime_now
from education.utils.singleton import Singleton


class SavedInstance(metaclass=Singleton):
    """
    Сохраненные данные модели для отслеживания изменений в модели до и после ее сохранения.
    """
    data = {}
    is_skip = False

    @staticmethod
    def save_obj(obj, attrs: list[str]):
        SavedInstance.data = {}
        for key in attrs:
            SavedInstance.data[key] = getattr(obj, key)

    @staticmethod
    def clear():
        SavedInstance.data.clear()


def add_current_user(func):
    @wraps(func)
    def wrapper(sender, instance, **kwargs):
        kwargs['current_user'] = LoggedInUser().current_user
        return func(sender, instance, **kwargs)

    return wrapper


def create_notice(user_id: int, notice_code: NoticeCode, kwargs: dict = None):
    Notice.objects.create(user_id=user_id,
                          notice_type_id=NoticeType.objects.get(code=notice_code.value).id,
                          kwargs=json.dumps(kwargs) if kwargs else None)


def create_or_update_student_achievement(student_id: int,
                                         achievement_code: AchievementCode,
                                         date_receiving: datetime.date = None,
                                         value: int = None,
                                         level: int = None):
    if not date_receiving:
        date_receiving = datetime_now().date()

    achievement = Achievement.objects.get(code=achievement_code.value)
    achievement_levels = AchievementLevel.objects.filter(achievement_id=achievement.id).order_by('-level')

    for achievement_level in achievement_levels:
        if (not achievement_level.required_value or
                (value and value >= achievement_level.required_value) or
                (level and level == achievement_level.level)):

            student_achievement = get_model_or_none(StudentAchievement,
                                                    student_id=student_id,
                                                    achievement_id=achievement.id)

            if student_achievement:
                if student_achievement.level != achievement_level.level:
                    student_achievement.level = achievement_level.level
                    student_achievement.save()
            else:
                StudentAchievement.objects.create(student_id=student_id,
                                                  level=achievement_level.level,
                                                  date_receiving=date_receiving,
                                                  achievement_id=achievement.id)
            break


def proc_hashtags_for_model(instance):
    if SavedInstance.is_skip:
        SavedInstance.is_skip = False
        return

    if instance.hashtag_list:
        instance.hashtag_list.delete()
        instance.hashtag_list = None

    instance.text = instance.text.strip()
    SavedInstance.is_skip = True
    instance.save()

    # Создать сущности в БД для хештегов, которые расположены в конце текста
    for word in reversed(instance.text.split()):
        if len(word) > 1 and word[0] == '#':
            if not instance.hashtag_list:
                instance.hashtag_list = HashtagList.objects.create()
                SavedInstance.is_skip = True
                instance.save()

            hashtag = Hashtag.objects.get_or_create(name=word[1:])[0]
            HashtagFromList.objects.create(hashtag_id=hashtag.id,
                                           hashtag_list_id=instance.hashtag_list.id)
        else:
            break


@receiver(post_save, sender=Notice)
def post_save_notice(sender, instance: Notice, **kwargs):
    # TODO интегрировать с telegram ботом:
    #  отправлять туда пользователю сообщение о новом уведомлении
    pass


@receiver(post_save, sender=User)
def post_create_user(sender, instance: User, **kwargs):
    """
    При создании пользователя для него создаются следующие модели:
    1. Активность пользователя;
    2. Личная информация;
    3. Личные настройки приложения;
    4. Запись в очередь на верификацию (если он не является персоналом).
    """
    if kwargs['created']:
        UserActivity.objects.create(datetime_last_activity=instance.date_joined,
                                    date_last_online=instance.date_joined.date(),
                                    user_id=instance.id)
        PersonalInformation.objects.create(user_id=instance.id)
        UserSettings.objects.create(user_id=instance.id)

        if not instance.is_staff:
            UserVerification.objects.create(user_id=instance.id)


@receiver(pre_save, sender=UserActivity)
def pre_save_user_activity(sender, instance: UserActivity, **kwargs):
    obj = get_model_or_none(UserActivity, id=instance.id)
    if obj:
        SavedInstance.data = {
            'online_days_in_a_row': obj.online_days_in_a_row,
        }


@receiver(post_save, sender=UserActivity)
def post_save_user_activity(sender, instance: UserActivity, **kwargs):
    if SavedInstance.is_skip:
        SavedInstance.is_skip = False
        return

    pre_online_days_in_a_row = SavedInstance.data.get('online_days_in_a_row')
    SavedInstance.clear()

    if instance.online_days_in_a_row != pre_online_days_in_a_row:
        student = get_model_or_none(Student, user_id=instance.user.id)
        if student:
            create_or_update_student_achievement(student_id=student.id,
                                                 achievement_code=AchievementCode.ONLINE_DAYS_IN_A_ROW,
                                                 value=instance.online_days_in_a_row)

    if instance.online_days_in_a_row > instance.online_days_in_a_row_max:
        instance.online_days_in_a_row_max = instance.online_days_in_a_row

    SavedInstance.is_skip = True
    instance.save()


@receiver(pre_save, sender=Student)
def pre_save_student(sender, instance: Student, **kwargs):
    if get_model_or_none(Teacher, user_id=instance.user_id):
        raise ValidationError(StringStorage.TEACHER_AND_STUDENT_PROHIBITED)

    obj = get_model_or_none(Student, id=instance.id)
    if obj:
        SavedInstance.data = {
            'points': obj.points,
            'coins': obj.coins,
            'rank_code': obj.rank.code,
        }


@receiver(post_save, sender=Student)
def post_save_student(sender, instance: Student, **kwargs):
    if SavedInstance.is_skip:
        SavedInstance.is_skip = False
        return

    pre_points = SavedInstance.data.get('points')
    pre_coins = SavedInstance.data.get('coins')
    pre_rank_code = SavedInstance.data.get('rank_code')
    SavedInstance.clear()

    if instance.points != pre_points:
        create_or_update_student_achievement(student_id=instance.id,
                                             achievement_code=AchievementCode.COLLECT_POINTS,
                                             value=instance.points)

        levels = Level.objects.filter(points__lte=instance.points).order_by('-points')
        if levels and levels[0].value != instance.level.value:
            instance.level = levels[0]
            create_notice(user_id=instance.user.id,
                          notice_code=NoticeCode.NEW_LEVEL,
                          kwargs={
                              'level': instance.level.value
                          })
            SavedInstance.is_skip = True
            instance.save()

    if kwargs['created']:
        Project.objects.create(student_id=instance.id,
                               status_id=ProjectStatus.objects.get(code=ProjectStatusCode.NONE.value).id)
        StudentActivity.objects.create(student_id=instance.id)

    else:
        if instance.rank.code != pre_rank_code:
            create_notice(user_id=instance.user.id,
                          notice_code=NoticeCode.UPDATE_RANK,
                          kwargs={
                              'rank_id': instance.rank.id,
                          })


@receiver(post_save, sender=UserVerification)
def post_create_user_verification(sender, instance: UserVerification, **kwargs):
    if not kwargs['created']:
        for user in User.objects.filter(is_staff=True):
            create_notice(user_id=user.id,
                          notice_code=NoticeCode.ADDED_USER_FOR_VERIFICATION,
                          kwargs={
                              'user_id': instance.id
                          })


@receiver(pre_delete, sender=UserVerification)
def pre_delete_user_verification(sender, instance: UserVerification, **kwargs):
    create_notice(user_id=instance.user.id,
                  notice_code=NoticeCode.USER_VERIFIED)


@receiver(post_save, sender=PersonalInformation)
def post_save_personal_information(sender, instance: PersonalInformation, **kwargs):
    if instance.image and instance.cover_image and instance.birthday and instance.about_me:
        create_or_update_student_achievement(student_id=Student.objects.get(user_id=instance.user.id).id,
                                             achievement_code=AchievementCode.FILL_PERSONAL_INFORMATION)


@receiver(pre_delete, sender=PointsAdditional)
def pre_delete_points_additional(sender, instance, **kwargs):
    if instance.points:
        instance.student.points -= instance.points
        instance.student.save()


@receiver(pre_save, sender=PointsAdditional)
def pre_save_points_additional(sender, instance, **kwargs):
    obj = get_model_or_none(PointsAdditional, id=instance.id)
    if obj:
        SavedInstance.data = {
            'points': obj.points,
        }


@receiver(post_save, sender=PointsAdditional)
def post_save_points_additional(sender, instance, **kwargs):
    pre_points = SavedInstance.data.get('points') or 0
    SavedInstance.clear()

    if pre_points != instance.points:
        instance.student.points += instance.points - pre_points
        instance.student.save()

    if kwargs['created']:
        create_notice(user_id=instance.user.id,
                      notice_code=NoticeCode.ADDITIONAL_POINTS_RECEIVED,
                      kwargs={
                          'points_additional_id': instance.id,
                      })


@receiver(pre_delete, sender=Test)
def pre_delete_test(sender, instance: Test, **kwargs):
    if instance.comment_list:
        instance.comment_list.delete()


@receiver(pre_delete, sender=TestResult)
def pre_delete_test_result(sender, instance: TestResult, **kwargs):
    SavedInstance.data = {
        'points': instance.points,
        'penalty_points': instance.penalty_points,
        'completed': instance.completed,
        'open_results': instance.assigned_test.open_results,
    }


@receiver(pre_save, sender=TestResult)
def pre_save_test_result(sender, instance: TestResult, **kwargs):
    obj = get_model_or_none(TestResult, id=instance.id)
    if obj:
        SavedInstance.data = {
            'points': obj.points,
            'penalty_points': obj.penalty_points,
            'completed': obj.completed,
            'open_results': obj.open_results,
        }


@receiver(post_save, sender=TestResult)
def post_save_test_result(sender, instance: TestResult, **kwargs):
    pre_points = SavedInstance.data.get('points') or 0
    pre_penalty_points = SavedInstance.data.get('penalty_points') or 0
    pre_completed = SavedInstance.data.get('completed')
    pre_open_answers = SavedInstance.data.get('open_results')
    SavedInstance.clear()
    SavedInstance.clear()

    if instance.datetime_complete:
        test_penalty_delay_list = TestPenaltyDelay.objects.all()

        if test_penalty_delay_list:
            test_penalty_delay = test_penalty_delay_list[0]

            seconds = (instance.datetime_complete - instance.datetime_begin).total_seconds()
            count = int(test_penalty_delay.seconds / seconds)
            instance.penalty_points = count * test_penalty_delay.points_loss_percent / 100.0 * instance.points

        else:
            instance.penalty_points = 0

    if (pre_completed and instance.completed and
            pre_open_answers and instance.assigned_test.open_results):
        # Только изменения в баллах.
        instance.student.points += (instance.points - pre_points) - (instance.penalty_points - pre_penalty_points)

    elif ((instance.completed and instance.assigned_test.open_results) and
          (not pre_completed or not pre_open_answers)):
        # Результаты теста были открыты.
        instance.student.points += instance.points - instance.penalty_points

    elif ((not instance.completed or not instance.assigned_test.open_results) and
          (pre_completed and pre_open_answers)):
        # Результаты теста были закрыты.
        instance.student.points -= pre_points - pre_penalty_points

    if instance.completed and instance.assigned_test.open_results:
        # Тест сдан.
        create_or_update_student_achievement(student_id=instance.student.id,
                                             achievement_code=AchievementCode.BEST_TEST_RESULT,
                                             value=round(instance.points / instance.assigned_test.test.points * 100))

    instance.student.save()


@receiver(pre_delete, sender=TestTask)
def pre_delete_test_task(sender, instance: TestTask, **kwargs):
    if instance.points:
        instance.test.points -= instance.points
        instance.test.save()


@receiver(pre_save, sender=TestTask)
def pre_save_test_task(sender, instance: TestTask, **kwargs):
    obj = get_model_or_none(TestTask, id=instance.id)
    if obj:
        SavedInstance.data = {
            'points': obj.points,
        }


@receiver(post_save, sender=TestTask)
def post_save_test_task(sender, instance: TestTask, **kwargs):
    pre_points = SavedInstance.data.get('points') or 0
    SavedInstance.clear()

    if pre_points != instance.points:
        instance.test.points += instance.points - pre_points
        instance.test.save()


@receiver(pre_delete, sender=TestTaskAnswer)
def pre_delete_test_task(sender, instance: TestTaskAnswer, **kwargs):
    if instance.points:
        test_result = TestResult.objects.filter(assigned_test__test_id=instance.test_task.test.id,
                                                student_id=instance.student.id)
        test_result[0].points -= instance.points
        test_result[0].save()


@receiver(pre_save, sender=TestTaskAnswer)
def pre_save_test_task_answer(sender, instance: TestTaskAnswer, **kwargs):
    obj = get_model_or_none(TestTaskAnswer, id=instance.id)
    if obj:
        SavedInstance.data = {
            'points': obj.points,
        }


@receiver(post_save, sender=TestTaskAnswer)
def post_save_test_task_answer(sender, instance: TestTaskAnswer, **kwargs):
    pre_points = SavedInstance.data.get('points') or 0
    SavedInstance.clear()

    if pre_points != instance.points:
        test_result = TestResult.objects.filter(assigned_test__test_id=instance.test_task.test.id,
                                                student_id=instance.student.id)
        test_result[0].points += instance.points - pre_points
        test_result[0].save()


@receiver(post_save, sender=HappyBirthday)
def post_create_happy_birthday(sender, instance: HappyBirthday, **kwargs):
    if kwargs['created']:
        create_notice(user_id=instance.personal_information.user.id,
                      notice_code=NoticeCode.HAPPY_BIRTHDAY)


@receiver(pre_delete, sender=Project)
def pre_delete_project(sender, instance: Project, **kwargs):
    if instance.comment_list:
        instance.comment_list.delete()


@receiver(pre_save, sender=Project)
def pre_save_project(sender, instance: Project, **kwargs):
    obj = get_model_or_none(Project, id=instance.id)
    if obj:
        SavedInstance.data = {
            'name': obj.name,
            'status_code': obj.status.code,
        }


@receiver(post_save, sender=Project)
@add_current_user
def post_save_project(sender, instance: Project, **kwargs):
    if SavedInstance.is_skip:
        SavedInstance.is_skip = False
        return

    pre_name = SavedInstance.data.get('name')
    pre_status_code = SavedInstance.data.get('status_code')
    SavedInstance.clear()

    if kwargs['created']:
        return

    current_user = kwargs['current_user']

    if pre_name != instance.name and instance.student.user.id == current_user.id:
        for teacher in Teacher.objects.all():
            create_notice(user_id=teacher.user.id,
                          notice_code=NoticeCode.UPDATE_PROJECT_NAME,
                          kwargs={
                              'project_id': instance.id,
                              'project_name': instance.name,
                          })

        instance.status_id = ProjectStatus.objects.get(code=ProjectStatusCode.APPROVAL.value).id
        SavedInstance.is_skip = True
        instance.save()

    if pre_status_code != instance.status.code:
        create_notice(user_id=instance.student.user.id,
                      notice_code=NoticeCode.UPDATE_PROJECT_STATUS,
                      kwargs={
                          'project_id': instance.id,
                          'status_code': instance.status.code,
                      })

        if instance.status.code == ProjectStatusCode.COMPLETED.value:
            create_or_update_student_achievement(student_id=instance.student.id,
                                                 achievement_code=AchievementCode.PROJECT,
                                                 level=2)

        elif instance.status.code > ProjectStatusCode.APPROVAL.value:
            create_or_update_student_achievement(student_id=instance.student.id,
                                                 achievement_code=AchievementCode.PROJECT,
                                                 level=1)


@receiver(pre_save, sender=StudentAchievement)
def pre_save_student_achievement(sender, instance: StudentAchievement, **kwargs):
    achievement_levels = list(AchievementLevel.objects
                              .filter(achievement_id=instance.achievement.id)
                              .order_by('level'))

    if instance.level not in [x.level for x in achievement_levels]:
        instance.level = achievement_levels[-1].level

    obj = get_model_or_none(StudentAchievement, id=instance.id)
    if obj:
        SavedInstance.data = {
            'level': obj.level,
        }


@receiver(post_save, sender=StudentAchievement)
def post_save_student_achievement(sender, instance: StudentAchievement, **kwargs):
    pre_level = SavedInstance.data.get('level') or 0
    SavedInstance.clear()

    if kwargs['created'] or instance.level > pre_level:
        create_notice(user_id=instance.student.user.id,
                      notice_code=NoticeCode.ACHIEVEMENT_RECEIVED,
                      kwargs={
                          'achievement_id': instance.achievement.id,
                          'achievement_level': instance.level,
                      })

        # Уведомить администраторов о необходимости выдачи значка.
        achievement_levels = AchievementLevel.objects.filter(achievement_id=instance.achievement.id)
        for el in achievement_levels:
            if instance.level == el.level and el.badge_awarded:
                for user in User.objects.filter(is_staff=True):
                    create_notice(user_id=user.id,
                                  notice_code=NoticeCode.NEED_ISSUE_BADGE_FOR_ACHIEVEMENT,
                                  kwargs={
                                      'student_achievement_id': instance.id,
                                  })
                break


@receiver(post_save, sender=AssignedTask)
def post_create_assigned_task(sender, instance: AssignedTask, **kwargs):
    if kwargs['created']:
        for student in Student.objects.filter(group_id=instance.student_group_id):
            create_notice(user_id=student.user.id,
                          notice_code=NoticeCode.ASSIGNED_TASK,
                          kwargs={
                              'task_id': instance.task.id,
                          })


@receiver(pre_delete, sender=Task)
def pre_delete_task(sender, instance: Task, **kwargs):
    if instance.comment_list:
        instance.comment_list.delete()

    if instance.hashtag_list:
        instance.hashtag_list.delete()


@receiver(pre_save, sender=Task)
def pre_save_task(sender, instance: Task, **kwargs):
    obj = get_model_or_none(Task, id=instance.id)
    if obj:
        SavedInstance.data = {
            'text': obj.text,
        }


@receiver(post_save, sender=Task)
def post_save_task(sender, instance: Task, **kwargs):
    pre_text = SavedInstance.data.get('text')
    SavedInstance.clear()

    if pre_text != instance.text or kwargs['created']:
        proc_hashtags_for_model(instance)


@receiver(pre_delete, sender=CompletingTask)
def pre_delete_completing_task(sender, instance: CompletingTask, **kwargs):
    if instance.comment_list:
        instance.comment_list.delete()

    if instance.points:
        instance.student.points -= instance.points
        instance.student.save()


@receiver(pre_save, sender=CompletingTask)
def pre_save_completing_task(sender, instance: CompletingTask, **kwargs):
    obj = get_model_or_none(CompletingTask, id=instance.id)
    if obj:
        SavedInstance.data = {
            'points': obj.points,
            'status_code': obj.status.code,
            'kwargs': obj.kwargs,
            'datetime_sent': obj.datetime_sent,
        }


@receiver(post_save, sender=CompletingTask)
def post_save_completing_task(sender, instance: CompletingTask, **kwargs):
    if SavedInstance.is_skip:
        SavedInstance.is_skip = False
        return

    pre_points = SavedInstance.data.get('points') or 0
    pre_status_code = SavedInstance.data.get('status_code')
    pre_kwargs = SavedInstance.data.get('kwargs')
    pre_datetime_sent = SavedInstance.data.get('datetime_sent')
    SavedInstance.clear()

    pre_kwargs = pre_kwargs or {}
    kwargs = instance.kwargs or {}

    check = kwargs.get('check') if kwargs else None
    if check:
        kwargs.pop('check')

    # Если было изменение ответа.
    if ((pre_kwargs.get('text') != kwargs.get('text') and
         pre_kwargs.get('files') != kwargs.get('files') or check) and
            check is not False):

        instance.datetime_sent = datetime_now()
        checking_completing_task_list = CheckingCompletingTask.objects.filter(task_id=instance.assigned_task.task.id)
        
        # Если выполнение задачи проверяется автоматически.
        if checking_completing_task_list:
            status = TaskStatusCode.TESTS_PASSED
            
            for item in checking_completing_task_list:
                if item.on_a_background:
                    # Выполнить проверку в фоновом потоке.
                    ProcCheckingCompletingTask.objects.create(completing_task_id=instance.id,
                                                              checking_completing_task_id=item.id)
                    status = TaskStatusCode.UNDERGOING_TESTING
                else:
                    # Выполнить проверку сейчас.
                    func = CHECKING_COMPLETING_TASK_FUNC_BY_NAME[item.script.name]
                    result = func(instance, **item.kwargs)
                    if result is False:
                        status = TaskStatusCode.TESTS_FAILED
                        # Удалим все назначенные проверки для этого выполнения задания
                        for item_ in ProcCheckingCompletingTask.objects.filter(completing_task_id=instance.id):
                            item_.delete()
                        break
                    
            instance.status = TaskStatus.objects.get(code=status.value)

        # Если выполнение задачи проверяется вручную.
        elif instance.assigned_task.task.manual_check_result:
            instance.status = TaskStatus.objects.get(code=TaskStatusCode.REVIEW.value)
            
        else:
            instance.status = TaskStatus.objects.get(code=TaskStatusCode.DONE.value)
            instance.points = instance.assigned_task.task.points

        if instance.status.code != TaskStatusCode.REVIEW.value:
            # Отметка количества попыток.
            instance.total_attempts += 1
            if pre_datetime_sent and pre_datetime_sent != instance.datetime_sent:
                instance.attempts_today = 0
            instance.attempts_today += 1

    if pre_status_code != instance.status.code:
        if instance.status.code in (TaskStatusCode.TESTS_FAILED.value,
                                    TaskStatusCode.TESTS_PASSED.value,
                                    TaskStatusCode.RETURNED.value,
                                    TaskStatusCode.DONE.value):
            create_notice(user_id=instance.student.user.id,
                          notice_code=NoticeCode.UPDATE_COMPLETING_TASK_STATUS,
                          kwargs={
                              'task_id': instance.assigned_task.task.id,
                              'status_code': instance.status.code,
                          })
            instance.viewed = False

        if instance.status.code == TaskStatusCode.TESTS_PASSED.value:
            if instance.assigned_task.task.manual_check_result:
                instance.status = TaskStatus.objects.get(code=TaskStatusCode.REVIEW.value)
            else:
                instance.status = TaskStatus.objects.get(code=TaskStatusCode.DONE.value)

        elif (instance.status.code == TaskStatusCode.REVIEW.value and
              not instance.assigned_task.task.manual_check_result):
            instance.status = TaskStatus.objects.get(code=TaskStatusCode.DONE.value)

        if instance.status.code == TaskStatusCode.DONE.value:
            # Выполнение заданий в общем.
            count = (CompletingTask.objects
                     .filter(student_id=instance.student.id,
                             status__code=TaskStatusCode.DONE.value)
                     .count())
            create_or_update_student_achievement(student_id=instance.student.id,
                                                 achievement_code=AchievementCode.COMPLETE_TASKS,
                                                 value=count)

            # Выполнение сложных заданий.
            if instance.assigned_task.task.difficulty:
                if instance.assigned_task.task.difficulty.code == DifficultyCode.HARD.value:
                    difficulty_hard = Difficulty.objects.get(code=DifficultyCode.HARD.value)
                    count_hard = (CompletingTask.objects
                                  .filter(student_id=instance.student.id,
                                          status__code=TaskStatusCode.DONE.value,
                                          assigned_task__task__difficulty_id=difficulty_hard.id)
                                  .count())
                    create_or_update_student_achievement(student_id=instance.student.id,
                                                         achievement_code=AchievementCode.COMPLETE_HARD_TASKS,
                                                         value=count_hard)

            # Выполнено заданий подряд с первого раза.
            student_activity = StudentActivity.objects.get(student_id=instance.student.id)
            if instance.total_attempts == 1:
                student_activity.pass_tasks_first_time_in_a_row += 1

                # Фиксируем рекорд.
                if (student_activity.pass_tasks_first_time_in_a_row >
                        student_activity.pass_tasks_first_time_in_a_row_max):
                    student_activity.pass_tasks_first_time_in_a_row_max = \
                        student_activity.pass_tasks_first_time_in_a_row

                create_or_update_student_achievement(student_id=instance.student.id,
                                                     achievement_code=AchievementCode.COMPLETE_TASKS,
                                                     value=student_activity.pass_tasks_first_time_in_a_row)
            else:
                student_activity.pass_tasks_first_time_in_a_row = 0
            student_activity.save()

        elif pre_status_code == TaskStatusCode.DONE.value and instance.status.code != TaskStatusCode.DONE.value:
            instance.points = 0

    if pre_points != instance.points:
        instance.student.points += instance.points - pre_points
        instance.student.save()

    SavedInstance.is_skip = True
    instance.save()


@receiver(pre_save, sender=AssignedTest)
def pre_save_assigned_test(sender, instance: AssignedTest, **kwargs):
    obj = get_model_or_none(AssignedTest, id=instance.id)
    if obj:
        SavedInstance.data = {
            'is_open': obj.is_open,
            'open_results': obj.open_results,
        }


@receiver(post_save, sender=AssignedTest)
def post_save_assigned_test(sender, instance: AssignedTest, **kwargs):
    pre_is_open = SavedInstance.data.get('is_open')
    pre_open_results = SavedInstance.data.get('open_results')
    SavedInstance.clear()

    if kwargs['created']:
        for student in Student.objects.filter(group_id=instance.student_group_id):
            create_notice(user_id=student.user.id,
                          notice_code=NoticeCode.ASSIGNED_TEST,
                          kwargs={
                              'test_id': instance.test.id,
                          })

    else:
        if pre_is_open != instance.is_open:
            for student in Student.objects.filter(group_id=instance.student_group.id):
                create_notice(user_id=student.user.id,
                              notice_code=NoticeCode.UPDATE_TEST_OPEN_STATUS,
                              kwargs={
                                  'is_open': instance.is_open,
                                  'test_id': instance.test.id,
                              })

        elif pre_open_results != instance.open_results:
            for test_result in TestResult.objects.filter(assigned_test_id=instance.id):
                create_notice(user_id=test_result.student.user.id,
                              notice_code=NoticeCode.UPDATE_TEST_RESULTS_STATUS,
                              kwargs={
                                  'open_results': instance.open_results,
                                  'test_id': instance.test.id,
                              })
                # Уведомим TestResult об изменении open_results в assigned_test
                pre_save_test_result(TestResult, test_result)
                post_save_test_result(TestResult, test_result)


@receiver(post_save, sender=Feedback)
@add_current_user
def post_create_feedback(sender, instance: Feedback, **kwargs):
    if not kwargs['created']:
        return

    current_user = kwargs['current_user']
    if current_user:
        student = get_model_or_none(Student, user_id=current_user.id)
        if student:
            create_or_update_student_achievement(student_id=student.id,
                                                 achievement_code=AchievementCode.LEAVE_FEEDBACK)

    for user in User.objects.filter(is_staff=True):
        create_notice(user_id=user.id,
                      notice_code=NoticeCode.FEEDBACK_LEFT,
                      kwargs={
                          'feedback_id': instance.id
                      })


@receiver(post_save, sender=Comment)
def post_create_comment(sender, instance: Comment, **kwargs):
    if not kwargs['created']:
        return

    task = get_model_or_none(Task, comment_list_id=instance.comment_list.id)
    if task:
        for teacher in Teacher.objects.all():
            create_notice(user_id=teacher.user.id,
                          notice_code=NoticeCode.TASK_COMMENT_LEFT,
                          kwargs={
                              'comment_id': instance.id,
                              'task_id': task.id,
                          })
        return

    test = get_model_or_none(Test, comment_list_id=instance.comment_list.id)
    if test:
        for teacher in Teacher.objects.all():
            create_notice(user_id=teacher.user.id,
                          notice_code=NoticeCode.TEST_COMMENT_LEFT,
                          kwargs={
                              'comment_id': instance.id,
                              'test_id': task.id,
                          })
        return

    project = get_model_or_none(Project, comment_list_id=instance.comment_list.id)
    if project:
        create_notice(user_id=project.student.user.id,
                      notice_code=NoticeCode.PROJECT_COMMENT_LEFT,
                      kwargs={
                          'comment_id': instance.id,
                          'project_id': project.id,
                      })
        return

    completing_task = get_model_or_none(CompletingTask, comment_list_id=instance.comment_list.id)
    if completing_task:
        create_notice(user_id=completing_task.student.user.id,
                      notice_code=NoticeCode.COMPLETING_TASK_COMMENT_LEFT,
                      kwargs={
                          'comment_id': instance.id,
                          'task_id': completing_task.assigned_task.task.id,
                      })
        return


@receiver(pre_save, sender=System)
def pre_save_student_achievement(sender, instance: System, **kwargs):
    systems = System.objects.all()
    if systems:
        if instance.id != systems[0].id:
            raise ValidationError(StringStorage.SYSTEM_MUST_EXIST_ONLY_ONE_COPY)


@receiver(pre_delete, sender=Post)
def pre_delete_post(sender, instance: Post, **kwargs):
    if instance.comment_list:
        instance.comment_list.delete()

    if instance.hashtag_list:
        instance.hashtag_list.delete()


@receiver(pre_save, sender=Post)
def pre_save_post(sender, instance: Post, **kwargs):
    obj = get_model_or_none(Post, id=instance.id)
    if obj:
        SavedInstance.data = {
            'text': obj.text,
        }


@receiver(post_save, sender=Post)
def post_save_post(sender, instance: Post, **kwargs):
    pre_text = SavedInstance.data.get('text')
    SavedInstance.clear()

    if pre_text != instance.text or kwargs['created']:
        proc_hashtags_for_model(instance)


@receiver(pre_delete, sender=PostView)
def pre_delete_post_view(sender, instance: PostView, **kwargs):
    instance.post.count_views -= 1
    instance.post.save()


@receiver(post_save, sender=PostView)
def post_save_post_view(sender, instance: PostView, **kwargs):
    if kwargs['created']:
        instance.post.count_views += 1
        instance.post.save()


@receiver(post_save, sender=PostForStudentGroup)
def post_save_post_for_student_group(sender, instance: PostForStudentGroup, **kwargs):
    if kwargs['created']:
        for student in Student.objects.filter(group_id=instance.student_group_id):
            create_notice(user_id=student.user.id,
                          notice_code=NoticeCode.POST_ADDED,
                          kwargs={
                              'post_id': instance.post.id,
                          })


@receiver(post_save, sender=AssignedEvent)
def post_save_assigned_event(sender, instance: AssignedEvent, **kwargs):
    if kwargs['created']:
        for student in Student.objects.filter(group_id=instance.student_group_id):
            create_notice(user_id=student.user.id,
                          notice_code=NoticeCode.ASSIGNED_EVENT,
                          kwargs={
                              'event_id': instance.event.id,
                          })


@receiver(pre_save, sender=Teacher)
def pre_save_teacher(sender, instance: Teacher, **kwargs):
    if get_model_or_none(Student, user_id=instance.user_id):
        raise ValidationError(StringStorage.TEACHER_AND_STUDENT_PROHIBITED)


def signals():
    pass
