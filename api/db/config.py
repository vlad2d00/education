from enum import Enum


# ===========================================================
#                          Общее
# ===========================================================

PRINT_DB_LOGS = True

# Пути для сохранения файлов

ICONS_PATH_UPLOAD = 'icons/'
IMAGES_PATH_UPLOAD = 'images/'
FILES_PATH_UPLOAD = 'files/'
VIDEO_PATH_UPLOAD = 'video/'


# Пагинация

PAGE_LIMIT_DEFAULT = 10
PAGE_LIMIT_MAX = 1000


# Админ панель

ADMIN_PAGE_SIZE = 50
ADMIN_CROPPED_TEXT_SIZE = 50


# Web

IMAGE_TEMPLATE_FORMAT = 'web/images/{}.html'
WEB_TEMPLATE_FORMAT = 'web/pages/{}.html'

WEB_IMAGES_PATH = 'web/templates/web/images/'
WEB_PERMISSIONS_FOLDER_NAME = 'permissions'


# ===========================================================
#                         Длины строк
# ===========================================================

# Общее

NAME_MAX_LENGTH = 70
SHORT_NAME_MIN_LENGTH = 2
SHORT_NAME_MAX_LENGTH = 30
FILE_NAME_MAX_LENGTH = 255


# Пользователи

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 100
FIRST_LAST_NAME_MIN_LENGTH = 2
FIRST_LAST_NAME_MAX_LENGTH = 30


# Тексты

ABOUT_ME_MAX_LENGTH = 150
URL_MAX_LENGTH = 2048
HEADER_MAX_LENGTH = 150
MESSAGE_MAX_LENGTH = 4096
TEXT_MAX_LENGTH = 16384


# Системное

IP_ADDRESS_MAX_LENGTH = 45
ARGS_MAX_LENGTH = 1024
PATH_MAX_LENGTH = 255
USER_AGENT_MAX_LENGTH = 255
VERSION_MAX_LENGTH = 20


# ===========================================================
#               Перечисления, используемые в коде
# ===========================================================

class TaskStatusCode(Enum):
    ASSIGNED = 0
    UNDERGOING_TESTING = 1
    TESTS_FAILED = 2
    TESTS_PASSED = 3
    REVIEW = 4
    RETURNED = 5
    DONE = 6


class ProjectStatusCode(Enum):
    NONE = 0
    RETURNED = 1
    APPROVAL = 2
    DESIGN_DEVELOPMENT = 3
    USE_CASE_DEVELOPMENT = 4
    APP_DEVELOPMENT = 5
    COMPLETED = 6


class RankCode(Enum):
    ORDINARY = 0
    UNUSUAL = 1
    RARE = 2
    UNIQUE = 3
    LEGENDARY = 4

    COPPER = 10
    SILVER = 11
    GOLD = 12


class MarkCode(Enum):
    THREE = 3
    FOUR = 4
    FIVE = 5


class DifficultyCode(Enum):
    EASY = 0
    NORMAL = 1
    MEDIUM = 2
    HARD = 3


class AnswerFormatCode(Enum):
    NONE = 0
    TEXT = 1
    FILES = 2
    TEXT_AND_FILES = 3
    PROGRAM_TEXT = 4
    PROGRAM_TEXT_AND_FILES = 5


class NoticeCode(Enum):
    # Для персонала и преподавателей:
    ADDED_USER_FOR_VERIFICATION = 100
    FEEDBACK_LEFT = 101
    NEED_ISSUE_BADGE_FOR_ACHIEVEMENT = 102
    UPDATE_PROJECT_NAME = 103
    TASK_COMMENT_LEFT = 104
    TEST_COMMENT_LEFT = 105

    # Для студентов личные:
    USER_VERIFIED = 200
    HAPPY_BIRTHDAY = 201
    NEW_LEVEL = 202
    UPDATE_PROJECT_STATUS = 203
    ACHIEVEMENT_RECEIVED = 204
    UPDATE_RANK = 205
    UPDATE_COMPLETING_TASK_STATUS = 206
    ADDITIONAL_POINTS_RECEIVED = 207
    PROJECT_COMMENT_LEFT = 208
    COMPLETING_TASK_COMMENT_LEFT = 209

    # Для студентов групповые:
    POST_ADDED = 300
    ASSIGNED_EVENT = 301
    ASSIGNED_TASK = 302
    ASSIGNED_TEST = 303
    UPDATE_TEST_OPEN_STATUS = 304
    UPDATE_TEST_RESULTS_STATUS = 305


class AchievementCode(Enum):
    FILL_PERSONAL_INFORMATION = 1
    LEAVE_FEEDBACK = 2
    LEAVE_COMMENT = 3
    PROJECT = 4
    ONLINE_DAYS_IN_A_ROW = 5
    BEST_TEST_RESULT = 6
    PASS_TASKS_FIRST_TIME_IN_A_ROW = 7
    COLLECT_POINTS = 8
    COMPLETE_TASKS = 9
    COMPLETE_HARD_TASKS = 10
    COLLECT_COINS = 11
