import json

from django.contrib import admin
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin

from api.models import *

admin.site.site_header = 'Панель администрированея'


@admin.register(System)
class SystemAdmin(ImportExportModelAdmin):
    list_display = ('version', 'hide_rating')
    list_display_links = ('version',)
    list_editable = ('hide_rating',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(TechnicalWork)
class TechnicalWorkAdmin(ImportExportModelAdmin):
    list_display = ('id', 'datetime_begin', 'datetime_end', 'description')
    fields = (('datetime_begin', 'datetime_end'), 'description')
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(LinkGroup)
class LinkGroupAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'position')
    list_display_links = ('name',)
    list_editable = ('position',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(Link)
class LinkAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'group', 'cropped_url', 'cropped_description', 'position')
    list_display_links = ('name',)
    list_editable = ('position',)
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Описание')
    def cropped_url(self, obj):
        return get_cropped_text(obj.url, max_size=ADMIN_CROPPED_TEXT_SIZE)

    @admin.display(description='Описание')
    def cropped_description(self, obj):
        return get_cropped_text(obj.description, max_size=ADMIN_CROPPED_TEXT_SIZE)


@admin.register(Mark)
class MarkAdmin(ImportExportModelAdmin):
    list_display = ('name', 'value', 'complete_percent')
    list_display_links = ('name',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(TestPenaltyDelay)
class TestPenaltyDelayAdmin(ImportExportModelAdmin):
    list_display = ('seconds', 'points_loss_percent')
    list_display_links = ('seconds',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(BlockedUser)
class BlockedUserAdmin(ImportExportModelAdmin):
    list_display = ('user', 'datetime_unlock', 'cropped_cause')
    list_display_links = ('user',)
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Причина')
    def cropped_cause(self, obj):
        return get_cropped_text(obj.cause, max_size=ADMIN_CROPPED_TEXT_SIZE)


@admin.register(NoticeType)
class NoticeTypeAdmin(ImportExportModelAdmin):
    list_display = ('code', 'name')
    list_display_links = ('name',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(Notice)
class NoticeAdmin(ImportExportModelAdmin):
    list_display = ('id', 'datetime_create', 'user', 'notice_type', 'kwargs', 'is_read')
    list_display_links = ('user',)
    list_filter = ('notice_type', 'is_read')
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Словарь аргументов')
    def kwargs_keys(self, obj):
        return list(json.loads(obj.kwargs).keys()) if obj.kwargs else None


@admin.register(IPAddress)
class IPAddressAdmin(ImportExportModelAdmin):
    list_display = ('value', 'last_minute_requests')
    list_display_links = ('value',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(BlockedIPAddress)
class BlockedIPAddressAdmin(ImportExportModelAdmin):
    list_display = ('datetime_unlock', 'ip_address', 'cause')
    list_display_links = ('ip_address',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(UserAgent)
class UserAgentAdmin(ImportExportModelAdmin):
    list_display = ('value',)
    list_display_links = ('value',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(RequestMethod)
class RequestMethodAdmin(ImportExportModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(Log)
class LogAdmin(ImportExportModelAdmin):
    list_display = (
        'datetime_create', 'path', 'method', 'status_code', 'user', 'kwargs_keys', 'ip_address', 'user_agent')
    list_display_links = ('datetime_create',)
    list_filter = ('method', 'status_code')
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Словарь аргументов')
    def kwargs_keys(self, obj):
        return list(json.loads(obj.kwargs).keys()) if obj.kwargs else None


@admin.register(UserActionType)
class UserActionTypeAdmin(ImportExportModelAdmin):
    list_display = ('code', 'name')
    list_display_links = ('name',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(UserAction)
class UserActionAdmin(ImportExportModelAdmin):
    list_display = ('datetime_create', 'user', 'action_type', 'kwargs')
    list_display_links = ('datetime_create',)
    list_filter = ('action_type',)
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Словарь аргументов')
    def kwargs_keys(self, obj):
        return list(json.loads(obj.kwargs).keys()) if obj.kwargs else None


@admin.register(UserActivity)
class UserActivityAdmin(ImportExportModelAdmin):
    list_display = ('user', 'datetime_last_activity', 'online_days_in_a_row', 'online_days_in_a_row_max')
    list_display_links = ('user',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(PersonalInformation)
class PersonalInformationAdmin(ImportExportModelAdmin):
    list_display = ('user', 'show_image', 'show_cover_image', 'birthday', 'cropped_about_me')
    list_display_links = ('user',)
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Аватарка')
    def show_image(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width=80>') if obj.image else None

    @admin.display(description='Обложка')
    def show_cover_image(self, obj):
        return mark_safe(f'<img src="{obj.cover_image.url}" width=240>') if obj.cover_image else None

    @admin.display(description='О себе')
    def cropped_about_me(self, obj):
        return get_cropped_text(obj.about_me, max_size=ADMIN_CROPPED_TEXT_SIZE) if obj.about_me else None


@admin.register(IntegrationTelegram)
class IntegrationTelegramAdmin(ImportExportModelAdmin):
    list_display = ('user', 'telegram_username', 'connect', 'connection_status')
    list_display_links = ('user',)
    list_filter = ('connect', 'connection_status')
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(UserSettings)
class UserSettingsAdmin(ImportExportModelAdmin):
    list_display = ('user', 'dark_theme', 'show_background_image')
    list_display_links = ('user',)
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Фоновое изображение')
    def show_background_image(self, obj):
        return mark_safe(f'<img src="{obj.background_image.url}" width=120>') if obj.background_image else None


@admin.register(HappyBirthday)
class HappyBirthdayAdmin(ImportExportModelAdmin):
    list_display = ('user', 'age')
    list_display_links = ('user',)
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Пользователь')
    def user(self, obj):
        return obj.personal_information.user


@admin.register(UserVerification)
class UserVerificationAdmin(ImportExportModelAdmin):
    list_display = ('user', 'rejected', 'rejection_cause')
    list_display_links = ('user',)
    list_editable = ('rejected', 'rejection_cause')
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(HashtagList)
class HashtagListAdmin(ImportExportModelAdmin):
    list_display = ('id', 'items')
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Хештеги')
    def items(self, obj):
        return [x.hashtag.name for x in HashtagFromList.objects.filter(hashtag_list_id=obj.id)]


@admin.register(Hashtag)
class HashtagAdmin(ImportExportModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(HashtagFromList)
class HashtagFromListAdmin(ImportExportModelAdmin):
    list_display = ('hashtag', 'hashtag_list')
    list_display_links = ('hashtag',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(CommentList)
class CommentListAdmin(ImportExportModelAdmin):
    list_display = ('id', 'count')
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Количество комментариев')
    def count(self, obj):
        return Comment.objects.filter(comment_list_id=obj.id).count()


@admin.register(Comment)
class CommentAdmin(ImportExportModelAdmin):
    list_display = ('datetime_create', 'user', 'cropped_text', 'is_read', 'comment_list', 'nested_comment')
    list_display_links = ('user',)
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Текст')
    def cropped_text(self, obj):
        return get_cropped_text(obj.text, max_size=ADMIN_CROPPED_TEXT_SIZE) if obj.about_me else None


@admin.register(Teacher)
class TeacherAdmin(ImportExportModelAdmin):
    list_display = ('user',)
    list_display_links = ('user',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(StudentGroup)
class StudentGroupAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(Level)
class LevelAdmin(ImportExportModelAdmin):
    list_display = ('value', 'points')
    list_display_links = ('value',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(Rank)
class RankAdmin(ImportExportModelAdmin):
    list_display = ('code', 'name')
    list_display_links = ('name',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    list_display = ('user', 'group', 'points', 'level', 'option', 'coins', 'rank')
    list_display_links = ('user',)
    list_filter = ('rank', 'group')
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(StudentActivity)
class StudentActivityAdmin(ImportExportModelAdmin):
    list_display = ('student', 'pass_tasks_first_time_in_a_row', 'pass_tasks_first_time_in_a_row_max')
    list_display_links = ('student',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(ProjectStatus)
class ProjectStatusAdmin(ImportExportModelAdmin):
    list_display = ('name', 'code')
    list_display_links = ('name',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    list_display = ('id', 'student', 'name', 'document_url', 'figma_url', 'drawio_url', 'github_url', 'status')
    list_display_links = ('name',)
    list_filter = ('student__group',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(Lesson)
class LessonAdmin(ImportExportModelAdmin):
    list_display = ('date', 'student_group', 'name', 'number')
    list_display_links = ('name',)
    list_filter = ('student_group',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(LessonPresence)
class LessonPresenceAdmin(ImportExportModelAdmin):
    list_display = ('student', 'lesson')
    list_display_links = ('student',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(Feedback)
class FeedbackAdmin(ImportExportModelAdmin):
    list_display = ('id', 'datetime_create', 'text', 'student_group', 'is_read')
    list_display_links = ('text',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(PointsAdditional)
class PointsAdditionalAdmin(ImportExportModelAdmin):
    list_display = ('date_receiving', 'student', 'points', 'comment')
    list_display_links = ('student',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(AchievementProgressScript)
class AchievementProgressScriptAdmin(ImportExportModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(Achievement)
class AchievementAdmin(ImportExportModelAdmin):
    list_display = ('id', 'code', 'name', 'icon_name', 'description', 'is_private', 'is_systemic', 'progress_script')
    list_display_links = ('name',)
    list_filter = ('is_private', 'is_systemic')
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(AchievementLevel)
class AchievementLevelAdmin(ImportExportModelAdmin):
    list_display = ('achievement', 'name', 'description', 'level', 'rank', 'required_value', 'badge_awarded')
    list_display_links = ('achievement',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(StudentAchievement)
class StudentAchievementAdmin(ImportExportModelAdmin):
    list_display = ('date_receiving', 'student', 'achievement', 'level', 'viewed')
    list_display_links = ('student',)
    list_filter = ('level', 'achievement')
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(CourseSection)
class CourseSectionAdmin(ImportExportModelAdmin):
    list_display = ('name', 'show_image', 'position')
    list_display_links = ('name',)
    list_editable = ('position',)
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Иконка')
    def show_image(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width=80>') if obj.image else None


@admin.register(Difficulty)
class DifficultyAdmin(ImportExportModelAdmin):
    list_display = ('code', 'name')
    list_display_links = ('name',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(AnswerFormat)
class AnswerFormatAdmin(ImportExportModelAdmin):
    list_display = ('code', 'name')
    list_display_links = ('name',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(FileList)
class FileListAdmin(ImportExportModelAdmin):
    list_display = ('id', 'items')
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Файлы')
    def items(self, obj):
        return [x.file.name for x in File.objects.filter(file_list_id=obj.id)]


@admin.register(File)
class FileAdmin(ImportExportModelAdmin):
    list_display = ('id', 'datetime_create', 'file')
    list_display_links = ('file',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(Task)
class TaskAdmin(ImportExportModelAdmin):
    list_display = ('id', 'datetime_create', 'name', 'show_image', 'course_section', 'difficulty', 'answer_format', 'points')
    list_display_links = ('name',)
    list_filter = ('course_section', 'difficulty', 'answer_format')
    list_editable = ('course_section', 'difficulty', 'answer_format', 'points')
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Иконка')
    def show_image(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width=80>') if obj.image else None


@admin.register(AssignedTask)
class AssignedTaskAdmin(ImportExportModelAdmin):
    list_display = ('datetime_create', 'task', 'student_group', 'readline', 'deadline')
    list_display_links = ('task',)
    list_filter = ('student_group',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(TaskStatus)
class TaskStatusAdmin(ImportExportModelAdmin):
    list_display = ('code', 'name')
    list_display_links = ('name',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(CompletingTask)
class CompletingTaskAdmin(ImportExportModelAdmin):
    list_display = ('id', 'datetime_sent', 'student', 'assigned_task', 'status', 'points', 'viewed')
    list_display_links = ('student',)
    list_filter = ('assigned_task', 'status')
    list_editable = ('status', 'points')
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Словарь аргументов')
    def kwargs_keys(self, obj):
        return list(json.loads(obj.kwargs).keys()) if obj.kwargs else None


@admin.register(TaskAccessCheckScript)
class TaskAccessCheckScriptAdmin(ImportExportModelAdmin):
    list_display = ('name', 'icon_name', 'description', 'kwargs')
    list_display_links = ('name',)
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Словарь аргументов')
    def kwargs_keys(self, obj):
        return list(json.loads(obj.kwargs).keys()) if obj.kwargs else None


@admin.register(CheckingTaskAccess)
class CheckingTaskAccessAdmin(ImportExportModelAdmin):
    list_display = ('task', 'script', 'kwargs')
    list_display_links = ('task',)
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Словарь аргументов')
    def kwargs_keys(self, obj):
        return list(json.loads(obj.kwargs).keys()) if obj.kwargs else None


@admin.register(CompletingTaskCheckScript)
class CompletingTaskCheckScriptAdmin(ImportExportModelAdmin):
    list_display = ('name', 'icon_name', 'description', 'kwargs')
    list_display_links = ('name',)
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Словарь аргументов')
    def kwargs_keys(self, obj):
        return list(json.loads(obj.kwargs).keys()) if obj.kwargs else None


@admin.register(CheckingCompletingTask)
class CheckingCompletingTaskAdmin(ImportExportModelAdmin):
    list_display = ('task', 'script', 'kwargs', 'on_a_background')
    list_display_links = ('task',)
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Словарь аргументов')
    def kwargs_keys(self, obj):
        return list(json.loads(obj.kwargs).keys()) if obj.kwargs else None


@admin.register(ProcCheckingCompletingTask)
class ProcCheckingCompletingTaskAdmin(ImportExportModelAdmin):
    list_display = ('completing_task', 'checking_completing_task')
    list_display_links = ('completing_task',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(Test)
class TestAdmin(ImportExportModelAdmin):
    list_display = ('id', 'datetime_create', 'name', 'show_image', 'points', 'time', 'course_section',
                    'shuffle_order_tasks', 'shuffle_order_answers', 'enable_points')
    list_display_links = ('name',)
    list_filter = ('course_section',)
    list_editable = ('points', 'time', 'shuffle_order_tasks', 'shuffle_order_answers', 'enable_points')
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Иконка')
    def show_image(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width=80>') if obj.image else None


@admin.register(AssignedTest)
class AssignedTestAdmin(ImportExportModelAdmin):
    list_display = ('test', 'date', 'is_open', 'open_results', 'student_group')
    list_display_links = ('test',)
    list_filter = ('student_group',)
    list_editable = ('date', 'is_open', 'open_results')
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(TestResult)
class TestResultAdmin(ImportExportModelAdmin):
    list_display = ('id', 'student', 'assigned_test', 'datetime_begin', 'datetime_complete', 'completed',
                    'points', 'penalty_points', 'viewed')
    list_display_links = ('student',)
    list_filter = ('student__group',)
    list_editable = ('completed', 'points')
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(Event)
class EventAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'show_image', 'datetime_begin', 'datetime_end', 'points')
    list_display_links = ('name',)
    list_editable = ('datetime_begin', 'datetime_end', 'points')
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Иконка')
    def show_image(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width=80>') if obj.image else None


@admin.register(AssignedEvent)
class AssignedEventAdmin(ImportExportModelAdmin):
    list_display = ('event', 'datetime_begin_', 'datetime_end_', 'student_group')
    list_display_links = ('event',)
    list_filter = ('student_group',)
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Дата и время начала')
    def datetime_begin_(self, obj):
        return obj.datetime_begin or obj.event.datetime_begin

    @admin.display(description='Дата и время завершения')
    def datetime_end_(self, obj):
        return obj.datetime_end or obj.event.datetime_end


@admin.register(Post)
class PostAdmin(ImportExportModelAdmin):
    list_display = ('id', 'datetime_create', 'datetime_update', 'header', 'cropped_description',
                    'is_published', 'count_views')
    list_display_links = ('header',)
    list_filter = ('is_published',)
    list_editable = ('is_published',)
    list_per_page = ADMIN_PAGE_SIZE

    @admin.display(description='Описание')
    def cropped_description(self, obj):
        return get_cropped_text(obj.description, max_size=ADMIN_CROPPED_TEXT_SIZE)


@admin.register(PostForStudentGroup)
class PostForStudentGroupAdmin(ImportExportModelAdmin):
    list_display = ('post', 'student_group')
    list_display_links = ('post',)
    list_filter = ('student_group',)
    list_per_page = ADMIN_PAGE_SIZE


@admin.register(PostView)
class PostViewAdmin(ImportExportModelAdmin):
    list_display = ('post', 'user')
    list_display_links = ('post',)
    list_per_page = ADMIN_PAGE_SIZE
