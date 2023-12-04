import datetime
from enum import Enum


class ForbiddenCode(Enum):
    NONE = 0
    IP_ADDRESS = 1
    USER = 2


class TechnicalWorkException(Exception):
    def __init__(
            self,
            datetime_end: datetime.datetime
    ):
        self.datetime_end = datetime_end

    def __str__(self):
        return 'Server on technical work until ' + str(self.datetime_end)


class BlockedIPAddressException(Exception):
    code = ForbiddenCode.IP_ADDRESS.value

    def __init__(
            self,
            datetime_unlock: datetime,
            cause: str
    ):
        self.datetime_unlock = datetime_unlock
        self.cause = cause

    def __str__(self):
        return 'User is blocked until ' + str(self.datetime_unlock) + '. Cause: ' + self.cause


class BlockedUserException(Exception):
    code = ForbiddenCode.USER.value

    def __init__(
            self,
            datetime_unlock: datetime,
            cause: str
    ):
        self.datetime_unlock = datetime_unlock
        self.cause = cause

    def __str__(self):
        return 'IP address blocked until ' + str(self.datetime_unlock) + '. Cause: ' + self.cause


class UserVerificationException(Exception):
    def __init__(
            self,
            rejected: bool,
            rejection_cause: str = None
    ):
        self.rejected = rejected
        self.rejection_cause = rejection_cause

    def __str__(self):
        return ('User is not verified' +
                ('. Rejected' if self.rejected else '') +
                ('. Cause: ' + self.rejection_cause if self.rejection_cause else ''))


class PermissionDeniedException(Exception):
    def __str__(self):
        return f'Permission denied'


class PageNotFoundException(Exception):
    def __init__(
            self,
            path: str,
    ):
        self.path = path

    def __str__(self):
        return f'page {self.path} not found'
