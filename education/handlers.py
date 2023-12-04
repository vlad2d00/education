from logging import FileHandler


def send_error(msg: str):
    # TODO создать telegram бота и отправлять его администраторам уведомления об ошибках
    print(send_error.__name__ + ': ' + msg)


class TelegramHandler(FileHandler):
    def emit(self, record):
        super().emit(record)
        print('TelegramHandler: ' + str(record.args))
