from enum import Enum

from api.models import CompletingTask
from api.utils.strings_storage import StringStorage


def check_value(completing_task: CompletingTask, value: int):
    text = completing_task.kwargs.get('text')
    if not text:
        completing_task.kwargs['error'] = StringStorage.VOID_VALUE.value
        completing_task.save()
        return False

    if text.strip() != value:
        completing_task.kwargs['error'] = StringStorage.INCORRECT_VALUE.value
        completing_task.save()
        return False

    return True


def test_program(completing_task: CompletingTask, program_lang: str, test_id: int):
    # TODO привязять к сервису programtester
    return None


class CheckingCompletingTaskFunc(Enum):
    CHECK_VALUE = check_value
    TEST_PROGRAM = test_program


CHECKING_COMPLETING_TASK_FUNC_BY_NAME = {
    check_value.__name__: check_value,
    test_program.__name__: test_program,
}
