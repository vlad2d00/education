from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin

from education.utils.singleton import Singleton


class LoggedInUser(metaclass=Singleton):
    user = None

    def set_user(self, request):
        if request.user.is_authenticated:
            self.user = request.user

    @property
    def current_user(self) -> User | None:
        return self.user

    @property
    def have_user(self) -> bool:
        return self.user is not None


class LoggedInUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        logged_in_user = LoggedInUser()
        logged_in_user.set_user(request)
        return None
