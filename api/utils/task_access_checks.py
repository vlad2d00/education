from enum import Enum

from api.models import CompletingTask


def min_level(completing_task: CompletingTask, value: int) -> bool:
    return completing_task.student.level.value >= value


class CheckingTaskAccessFunc(Enum):
    MIN_LEVEL = min_level


CHECKING_TASK_ACCESS_FUNC_BY_NAME = {
    min_level.__name__: min_level,
}
