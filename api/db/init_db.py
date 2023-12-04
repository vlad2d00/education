from api.models import *
from api.utils.achievement_progress import AchievementProgressFunc
from api.utils.completing_task_checks import CheckingCompletingTaskFunc
from api.utils.strings_storage import StringStorage
from education.settings import is_runserver


def init_db():
    def _init_system():
        if not System.objects.exists():
            System.objects.create()

    def _init_task_status():
        for value in (
                (TaskStatusCode.ASSIGNED, StringStorage.ASSIGNED),
                (TaskStatusCode.UNDERGOING_TESTING, StringStorage.PROCESS_TESTING),
                (TaskStatusCode.TESTS_FAILED, StringStorage.TESTS_FAILED),
                (TaskStatusCode.TESTS_PASSED, StringStorage.TESTS_PASSED),
                (TaskStatusCode.REVIEW, StringStorage.REVIEW),
                (TaskStatusCode.RETURNED, StringStorage.RETURNED),
                (TaskStatusCode.DONE, StringStorage.DONE),
        ):
            if not TaskStatus.objects.filter(code=value[0].value):
                TaskStatus.objects.create(name=value[1].value,
                                          code=value[0].value)

    def _init_project_status():
        for value in (
                (ProjectStatusCode.NONE, StringStorage.NONE),
                (ProjectStatusCode.RETURNED, StringStorage.RETURNED),
                (ProjectStatusCode.APPROVAL, StringStorage.PROJECT_APPROVAL),
                (ProjectStatusCode.DESIGN_DEVELOPMENT, StringStorage.DESIGN_DEVELOPMENT),
                (ProjectStatusCode.USE_CASE_DEVELOPMENT, StringStorage.USE_CASE_DEVELOPMENT),
                (ProjectStatusCode.APP_DEVELOPMENT, StringStorage.APP_DEVELOPMENT),
        ):
            if not ProjectStatus.objects.filter(code=value[0].value):
                ProjectStatus.objects.create(name=value[1].value,
                                             code=value[0].value)

    def _init_rank():
        for value in (
                (RankCode.ORDINARY, StringStorage.ORDINARY),
                (RankCode.UNUSUAL, StringStorage.UNUSUAL),
                (RankCode.RARE, StringStorage.RARE),
                (RankCode.UNIQUE, StringStorage.UNIQUE),
                (RankCode.LEGENDARY, StringStorage.LEGENDARY),

                (RankCode.COPPER, StringStorage.COPPER),
                (RankCode.SILVER, StringStorage.SILVER),
                (RankCode.GOLD, StringStorage.GOLD),
        ):
            if not Rank.objects.filter(code=value[0].value):
                Rank.objects.create(name=value[1].value,
                                    code=value[0].value)

    def _init_mark():
        for value in (
                (MarkCode.THREE, StringStorage.MARK_THREE, 50),
                (MarkCode.FOUR, StringStorage.MARK_FOUR, 70),
                (MarkCode.FIVE, StringStorage.MARK_FIVE, 85),
        ):
            if not Mark.objects.filter(value=value[0].value):
                Mark.objects.create(value=value[0].value,
                                    name=value[1].value,
                                    complete_percent=value[2])

    def _init_difficulty():
        for value in (
                (DifficultyCode.EASY, StringStorage.EASY),
                (DifficultyCode.NORMAL, StringStorage.NORMAL),
                (DifficultyCode.MEDIUM, StringStorage.MEDIUM),
                (DifficultyCode.HARD, StringStorage.HARD),
        ):
            if not Difficulty.objects.filter(code=value[0].value):
                Difficulty.objects.create(code=value[0].value,
                                          name=value[1].value)

    def _init_answer_format():
        for value in (
                (AnswerFormatCode.NONE, StringStorage.VOID),
                (AnswerFormatCode.TEXT, StringStorage.TEXT),
                (AnswerFormatCode.FILES, StringStorage.FILES),
                (AnswerFormatCode.TEXT_AND_FILES, StringStorage.TEXT_AND_FILES),
                (AnswerFormatCode.PROGRAM_TEXT, StringStorage.PROGRAM_TEXT),
        ):
            if not AnswerFormat.objects.filter(code=value[0].value):
                AnswerFormat.objects.create(code=value[0].value,
                                            name=value[1].value)

    def _init_completing_task_check_script():
        for value in (
                (CheckingCompletingTaskFunc.CHECK_VALUE, StringStorage.CHECK_VALUE_DESCRIPTION, {
                    'value': 'Правильное значение',
                }),
                (CheckingCompletingTaskFunc.TEST_PROGRAM, StringStorage.TEST_PROGRAM_DESCRIPTION, {
                    'program_lang': 'Язык программирования',
                    'test_id': 'ID теста',
                }),
        ):
            if not CompletingTaskCheckScript.objects.filter(name=value[0].__name__):
                CompletingTaskCheckScript.objects.create(name=value[0].__name__,
                                                         description=value[1].value,
                                                         kwargs=value[2])

    def _init_notice_type():
        for value in (
                # Для персонала и преподавателей:
                (NoticeCode.ADDED_USER_FOR_VERIFICATION, StringStorage.ADDED_USER_FOR_VERIFICATION),
                (NoticeCode.FEEDBACK_LEFT, StringStorage.FEEDBACK_LEFT),
                (NoticeCode.NEED_ISSUE_BADGE_FOR_ACHIEVEMENT, StringStorage.NEED_ISSUE_BADGE_FOR_ACHIEVEMENT),
                (NoticeCode.UPDATE_PROJECT_NAME, StringStorage.UPDATE_PROJECT_NAME),
                (NoticeCode.TASK_COMMENT_LEFT, StringStorage.TASK_COMMENT_LEFT),
                (NoticeCode.TEST_COMMENT_LEFT, StringStorage.TEST_COMMENT_LEFT),

                # Для студентов личные:
                (NoticeCode.USER_VERIFIED, StringStorage.USER_VERIFIED),
                (NoticeCode.HAPPY_BIRTHDAY, StringStorage.HAPPY_BIRTHDAY),
                (NoticeCode.NEW_LEVEL, StringStorage.NEW_LEVEL),
                (NoticeCode.UPDATE_PROJECT_STATUS, StringStorage.UPDATE_PROJECT_STATUS),
                (NoticeCode.ACHIEVEMENT_RECEIVED, StringStorage.ACHIEVEMENT_RECEIVED),
                (NoticeCode.UPDATE_RANK, StringStorage.UPDATE_RANK),
                (NoticeCode.UPDATE_COMPLETING_TASK_STATUS, StringStorage.UPDATE_TASK_COMPLETE_STATUS),
                (NoticeCode.ADDITIONAL_POINTS_RECEIVED, StringStorage.ADDITIONAL_POINTS_RECEIVED),
                (NoticeCode.PROJECT_COMMENT_LEFT, StringStorage.PROJECT_COMMENT_LEFT),
                (NoticeCode.COMPLETING_TASK_COMMENT_LEFT, StringStorage.TASK_COMPLETE_COMMENT_LEFT),

                # Для студентов групповые:
                (NoticeCode.POST_ADDED, StringStorage.POST_ADDED),
                (NoticeCode.ASSIGNED_TASK, StringStorage.TASK_ASSIGNED),
                (NoticeCode.ASSIGNED_EVENT, StringStorage.EVENT_ADDED),
                (NoticeCode.ASSIGNED_TEST, StringStorage.TEST_ASSIGNED),
                (NoticeCode.UPDATE_TEST_OPEN_STATUS, StringStorage.UPDATE_TEST_OPEN_STATUS),
                (NoticeCode.UPDATE_TEST_RESULTS_STATUS, StringStorage.UPDATE_TEST_RESULTS_STATUS),
        ):
            if not NoticeType.objects.filter(code=value[0].value):
                NoticeType.objects.create(code=value[0].value,
                                          name=value[1].value)

    def _init_achievement_progress_script():
        for func_name in [x.value.__name__ for x in AchievementProgressFunc]:
            if not AchievementProgressScript.objects.filter(name=func_name):
                AchievementProgressScript.objects.create(name=func_name)

    def _init_achievement_level():
        class SystemAchievementLevel:
            def __init__(self,
                         rang: RankCode,
                         name: str = None,
                         description: str = None,
                         required_value=None,
                         badge_awarded: bool = False):
                self.rang = rang
                self.name = name
                self.description = description
                self.required_value = required_value
                self.badge_awarded = badge_awarded

        class SystemAchievement:
            def __init__(self,
                         code: AchievementCode,
                         name: str,
                         description: str = None,
                         levels: tuple[SystemAchievementLevel, ...] = None,
                         progress_func: AchievementProgressFunc = None):
                self.code = code
                self.name = name
                self.description = description
                self.levels = levels
                self.progress_func_name = progress_func

        achievements = (
            SystemAchievement(
                code=AchievementCode.FILL_PERSONAL_INFORMATION,
                name='Мир, я иду!',
                levels=(
                    SystemAchievementLevel(rang=RankCode.ORDINARY,
                                           description='Заполнить личную информацию в своем профиле.'),
                ),
            ),
            SystemAchievement(
                code=AchievementCode.LEAVE_FEEDBACK,
                name='Особое мнение',
                levels=(
                    SystemAchievementLevel(rang=RankCode.ORDINARY,
                                           description='Оставить обратную связь.'),
                ),
            ),
            SystemAchievement(
                code=AchievementCode.LEAVE_COMMENT,
                name='Комментатор',
                levels=(
                    SystemAchievementLevel(rang=RankCode.ORDINARY, required_value=3,
                                           description='Оставить три комментария.'),
                ),
            ),
            SystemAchievement(
                code=AchievementCode.PROJECT,
                name='Ладно, за работу!',
                description='Занимайся разработкой своего проекта.',
                levels=(
                    SystemAchievementLevel(rang=RankCode.UNUSUAL,
                                           description='Утвердить тему своего проекта.'),
                    SystemAchievementLevel(rang=RankCode.RARE,
                                           description='Создать свой проект.'),
                ),
            ),
            SystemAchievement(
                code=AchievementCode.ONLINE_DAYS_IN_A_ROW,
                name='Постоянный клиент',
                description='Заходи в это приложение регулярно.',
                progress_func=AchievementProgressFunc.ONLINE_DAYS_IN_A_ROW,
                levels=(
                    SystemAchievementLevel(rang=RankCode.ORDINARY, name='Бог любит троицу', required_value=3,
                                           description='Заходи в приложение 3 дня подряд.'),
                    SystemAchievementLevel(rang=RankCode.UNUSUAL, name='Неделя', required_value=7,
                                           description='Заходи в приложение неделю подряд.'),
                ),
            ),
            SystemAchievement(
                code=AchievementCode.BEST_TEST_RESULT,
                name='Сражение с самим собой',
                description='Сдай тест с как можно лучшим результатом.',
                progress_func=AchievementProgressFunc.BEST_TEST_RESULT,
                levels=(
                    SystemAchievementLevel(rang=RankCode.ORDINARY, name='Пополам',
                                           required_value=Mark.objects.get(
                                               value=MarkCode.THREE.value).complete_percent,
                                           description=f'Набери минимум 50% баллов за любой тест.'),
                    SystemAchievementLevel(rang=RankCode.UNUSUAL, name='Хорошист',
                                           required_value=Mark.objects.get(
                                               value=MarkCode.FOUR.value).complete_percent,
                                           description='Набери минимум 70% баллов за любой тест.'),
                    SystemAchievementLevel(rang=RankCode.RARE, name='Отличник',
                                           required_value=Mark.objects.get(
                                               value=MarkCode.FIVE.value).complete_percent,
                                           description='Набери минимум 85% баллов за любой тест.'),
                    SystemAchievementLevel(rang=RankCode.UNIQUE, name='Гений',
                                           required_value=100,
                                           badge_awarded=True,
                                           description='Набери 100% баллов за любой тест.'),
                ),
            ),
            SystemAchievement(
                code=AchievementCode.PASS_TASKS_FIRST_TIME_IN_A_ROW,
                name='Комбо',
                description='Сдавай задания с первой попытки не останавливаясь.',
                progress_func=AchievementProgressFunc.PASS_TASKS_FIRST_TIME_IN_A_ROW,
                levels=(
                    SystemAchievementLevel(rang=RankCode.ORDINARY, required_value=1, name='Начало положено',
                                           description='Сдай задание с первого раза.'),
                    SystemAchievementLevel(rang=RankCode.UNUSUAL, required_value=3, name='Тройня',
                                           description='Сдай 3 задания подряд с первого раза.'),
                    SystemAchievementLevel(rang=RankCode.RARE, required_value=7, name='Неостановимый',
                                           description='Сдай 7 заданий подряд с первого раза.'),
                    SystemAchievementLevel(rang=RankCode.UNIQUE, required_value=12, name='Королевское комбо',
                                           badge_awarded=True,
                                           description='Сдай 12 заданий подряд с первого раза.'),
                ),
            ),
            SystemAchievement(
                code=AchievementCode.COLLECT_POINTS,
                name='Путь к вершине',
                description='Набирай как можно больше баллов.',
                progress_func=AchievementProgressFunc.COLLECT_POINTS,
                levels=(
                    SystemAchievementLevel(rang=RankCode.ORDINARY, required_value=50, name='Полтинник',
                                           description='Набери 50 баллов.'),
                    SystemAchievementLevel(rang=RankCode.UNUSUAL, required_value=100, name='Соточка',
                                           badge_awarded=True,
                                           description='Набери 100 баллов.'),
                    SystemAchievementLevel(rang=RankCode.RARE, required_value=200, name='Железные двести',
                                           badge_awarded=True,
                                           description='Набери 200 баллов.'),
                    SystemAchievementLevel(rang=RankCode.UNIQUE, required_value=300, name='Тракторист',
                                           badge_awarded=True,
                                           description='Набери 300 баллов.'),
                ),
            ),
            SystemAchievement(
                code=AchievementCode.COMPLETE_TASKS,
                name='Практик',
                description='Выполняй задачки.',
                progress_func=AchievementProgressFunc.COMPLETE_TASKS,
                levels=(
                    SystemAchievementLevel(rang=RankCode.ORDINARY, required_value=3, name='Начинающий',
                                           description='Выполни 3 задания.'),
                    SystemAchievementLevel(rang=RankCode.UNUSUAL, required_value=15, name='Опытный',
                                           description='Выполни 15 заданий.'),
                    SystemAchievementLevel(rang=RankCode.RARE, required_value=40, name='Мастер',
                                           description='Выполни 40 заданий.'),
                    SystemAchievementLevel(rang=RankCode.UNIQUE, required_value=72, name='Гуру',
                                           badge_awarded=True,
                                           description='Выполни 72 задания.'),
                ),
            ),
            SystemAchievement(
                code=AchievementCode.COMPLETE_HARD_TASKS,
                name='Сквозь трудности',
                description='Выполняй сложные задачки как настоящий Чак Норрис.',
                progress_func=AchievementProgressFunc.COMPLETE_HARD_TASKS,
                levels=(
                    SystemAchievementLevel(rang=RankCode.ORDINARY, name='Первый шаг', required_value=1,
                                           description='Выполни сложное задание.'),
                    SystemAchievementLevel(rang=RankCode.UNUSUAL, name='Закаленный', required_value=5,
                                           description='Выполни 5 сложных заданий.'),
                    SystemAchievementLevel(rang=RankCode.RARE, name='Неудержимый', required_value=10,
                                           description='Выполни 10 сложных заданий.'),
                    SystemAchievementLevel(rang=RankCode.UNIQUE, name='Монстр', required_value=20,
                                           badge_awarded=True,
                                           description='Выполни 20 сложных заданий.'),
                ),
            ),
        )

        for el in achievements:
            achievement_list = Achievement.objects.filter(code=el.code.value)
            if achievement_list:
                achievement = achievement_list[0]
            else:
                achievement = Achievement.objects.create(code=el.code.value,
                                                         name=el.name,
                                                         description=el.description,
                                                         is_systemic=True)

            for j, el_level in enumerate(el.levels):
                level = j + 1
                if not AchievementLevel.objects.filter(achievement_id=achievement.id, level=level):
                    AchievementLevel.objects.create(level=level,
                                                    name=el_level.name,
                                                    description=el_level.description,
                                                    required_value=el_level.required_value,
                                                    badge_awarded=el_level.badge_awarded,
                                                    achievement_id=achievement.id,
                                                    rank_id=Rank.objects.get(code=el_level.rang.value).id)

    def _init_course_section():
        if not CourseSection.objects.exists():
            for i, name in enumerate((
                    'Основы программирования',
                    'Android-разработка'
            )):
                CourseSection.objects.create(name=name, position=i + 1)

    def _init_student_group():
        if not StudentGroup.objects.exists():
            for i in range(4):
                name = str(i + 1) + ' группа'
                StudentGroup.objects.create(name=name)

    def _init_level():
        if not Level.objects.exists():
            for i, point in enumerate((0, 25, 55, 90, 135, 185, 240, 300)):
                Level.objects.create(value=i + 1, points=point)

    def _init_testing_penalty_delay():
        if not TestPenaltyDelay.objects.exists():
            TestPenaltyDelay.objects.create(seconds=60, points_loss_percent=10)

    def _init_superuser():
        if not User.objects.filter(is_superuser=True, username='admin'):
            try:
                User.objects.create_user(username='admin', password='admin',
                                         first_name='Админ', last_name='Админович',
                                         is_staff=True, is_superuser=True)
            except User.DoesNotExist:
                pass

    if is_runserver():
        print('Database initializing...')

    _init_system()
    _init_task_status()
    _init_project_status()
    _init_rank()
    _init_mark()
    _init_difficulty()
    _init_answer_format()
    _init_completing_task_check_script()
    _init_notice_type()
    _init_achievement_progress_script()
    _init_achievement_level()
    _init_course_section()
    _init_student_group()
    _init_level()
    _init_testing_penalty_delay()
    _init_superuser()

    if is_runserver():
        print('Database initialized!')
