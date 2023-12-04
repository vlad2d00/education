from api.models import *


def get_online_days_in_a_row(student_id: int) -> int:
    student = Student.objects.get(id=student_id)
    return UserActivity.objects.get(user_id=student.user.id).online_days_in_a_row


def get_best_test_result(student_id: int) -> int:
    result = 0
    for test_result in TestResult.objects.filter(student_id=student_id):
        new_result = round(test_result.points / test_result.test_assigned.test.points * 100)
        if new_result > result:
            result = new_result

    return result


def get_pass_tasks_first_time_in_a_row(student_id: int) -> int:
    return StudentActivity.objects.get(student_id=student_id).pass_tasks_first_time_in_a_row


def get_collect_points(student_id: int) -> int:
    return Student.objects.get(student_id=student_id).points


def get_complete_tasks(student_id: int) -> int:
    return (CompletingTask.objects.
            filter(student_id=student_id,
                   status__code=TaskStatusCode.DONE)
            .count())


def get_complete_hard_tasks(student_id: int) -> int:
    difficulty_hard = Difficulty.objects.get(code=DifficultyCode.HARD.value)
    return (CompletingTask.objects
            .filter(student_id=student_id,
                    status__code=TaskStatusCode.DONE,
                    task_assigned__task__difficulty_id=difficulty_hard.id)
            .count())


def get_collect_coins(student_id: int) -> int:
    return Student.objects.get(student_id=student_id).coins


class AchievementProgressFunc(Enum):
    ONLINE_DAYS_IN_A_ROW = get_online_days_in_a_row
    BEST_TEST_RESULT = get_best_test_result
    PASS_TASKS_FIRST_TIME_IN_A_ROW = get_pass_tasks_first_time_in_a_row
    COLLECT_POINTS = get_collect_points
    COMPLETE_TASKS = get_complete_tasks
    COMPLETE_HARD_TASKS = get_complete_hard_tasks
    COLLECT_COINS = get_collect_coins


ACHIEVEMENT_PROGRESS_FUNCS_BY_NAME = {
    get_online_days_in_a_row.__name__: get_online_days_in_a_row,
    get_best_test_result.__name__: get_best_test_result,
    get_pass_tasks_first_time_in_a_row.__name__: get_pass_tasks_first_time_in_a_row,
    get_collect_points.__name__: get_collect_points,
    get_complete_tasks.__name__: get_complete_tasks,
    get_complete_hard_tasks.__name__: get_complete_hard_tasks,
    get_collect_coins.__name__: get_collect_coins,
}
