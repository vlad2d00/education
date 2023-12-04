import traceback

from django.http import Http404
from django.utils.deprecation import MiddlewareMixin

from api.utils.log import create_log
from education.utils.singleton import Singleton


class MiddlewareData(metaclass=Singleton):
    status_code = None


class SessionLogMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if MiddlewareData.status_code:
            status_code = MiddlewareData.status_code
            MiddlewareData.status_code = None
        else:
            status_code = 404 if isinstance(exception, Http404) else 500

        try:
            create_log(request, status_code)

        except Exception:
            error = traceback.format_exc()
            print(error)

        return

    def process_response(self, request, response):
        if not response.status_code >= 400:
            if MiddlewareData.status_code:
                status_code = MiddlewareData.status_code
                MiddlewareData.status_code = None
            else:
                status_code = response.status_code

            try:
                create_log(request, status_code)

            except Exception:
                error = traceback.format_exc()
                print(error)

        return response
