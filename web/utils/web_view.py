import os.path

from django.shortcuts import render, redirect

from api.db.config import WEB_TEMPLATE_FORMAT, WEB_PERMISSIONS_FOLDER_NAME
from api.db.dao import get_blocked_ip_address, get_blocked_user, get_technical_work, get_user_verification
from api.utils.log import log_error
from education.middleware.session_log import MiddlewareData
from education.utils.datetime_service import datetime_to_string_words, datetime_timezone, datetime_to_string_relative
from web.utils.exceptions import *
from api.utils.strings_storage import StringStorage


def update_context(request, title: str, context: dict = None) -> dict:
    """
    Наполнение контекста необходимыми данными для каждого ответа веб-запроса
    """
    if not context:
        context = {}

    if not context.get('title'):
        context['title'] = title

    return context


def web_view(title: str, template_name: str):
    """
    Обертка для каждого запроса в веб-версию
    """
    def inner(func):
        def validate_request(request):
            technical_work = get_technical_work(is_now=True)
            if technical_work and not (request.user.is_authenticated and request.user.is_staff):
                raise TechnicalWorkException(datetime_end=technical_work.datetime_end)

            blocked_ip_address = get_blocked_ip_address(request)
            if blocked_ip_address:
                raise BlockedIPAddressException(datetime_unlock=blocked_ip_address.datetime_unlock,
                                                cause=blocked_ip_address.cause)

            blocked_user = get_blocked_user(request)
            if blocked_user:
                raise BlockedUserException(datetime_unlock=blocked_user.datetime_unlock,
                                           cause=blocked_user.cause)

            user_verification = get_user_verification(request)
            if user_verification:
                raise UserVerificationException(rejected=user_verification.rejected,
                                                rejection_cause=user_verification.rejection_cause)

        def wrapper(request, *args, **kwargs):
            def exception_response(template_name__: str, context_: dict):
                context_ = update_context(request,
                                          title=StringStorage.PERMISSION_DENIED.value,
                                          context=context_)
                template_name__ = WEB_TEMPLATE_FORMAT.format(os.path.join(WEB_PERMISSIONS_FOLDER_NAME, template_name__))
                return render(request, template_name__, context=context_)

            try:
                validate_request(request)

                # Перенаправить на авторизацию, если пользователь не авторизован
                if not request.user.is_authenticated and request.path not in ('/login/', '/register/'):
                    return redirect('login')

                result = func(request, *args, **kwargs)

                if not result or type(result).__name__ == dict.__name__:
                    # Был возвращен словарь
                    context = update_context(context=result, title=title, request=request)
                    return render(request, WEB_TEMPLATE_FORMAT.format(template_name), context=context)
                else:
                    return result

            except TechnicalWorkException as e:
                MiddlewareData.status_code = 503
                dt = datetime_to_string_words(datetime_timezone(e.datetime_end))
                dt_relative = datetime_to_string_relative(e.datetime_end, show_words=True)

                return exception_response('technical_work', {
                    'title': StringStorage.TECHNICAL_WORK.value,
                    'hide_header': True,
                    'hide_navigation': True,
                    'datetime_end': dt + ' (' + dt_relative + ')',
                })

            except PermissionDeniedException as e:
                MiddlewareData.status_code = 403
                return exception_response('permission_denied', {
                    'title': StringStorage.PERMISSION_DENIED.value,
                })

            except BlockedIPAddressException as e:
                MiddlewareData.status_code = 403
                return exception_response('blocked', {
                    'title': StringStorage.YOUR_IP_ADDRESS_BLOCKED.value,
                    'hide_header': True,
                    'hide_navigation': True,
                    'datetime_unlock': datetime_to_string_words(datetime_timezone(e.datetime_unlock))
                    if e.datetime_unlock else None,
                    'cause': e.cause,
                })

            except BlockedUserException as e:
                MiddlewareData.status_code = 403
                return exception_response('blocked', {
                    'title': StringStorage.YOUR_ACCOUNT_BLOCKED.value,
                    'hide_navigation': True,
                    'datetime_unlock': datetime_to_string_words(datetime_timezone(e.datetime_unlock))
                    if e.datetime_unlock else None,
                    'cause': e.cause,
                })

            except UserVerificationException as e:
                MiddlewareData.status_code = 403
                return exception_response('not_verified', {
                    'title': (StringStorage.USER_NOT_VERIFIED.value if e.rejected else
                              StringStorage.USER_WAITING_FOR_VERIFICATION.value),
                    'hide_navigation': True,
                    'rejected': e.rejected,
                    'rejection_cause': e.rejection_cause,
                })

            except PageNotFoundException as e:
                MiddlewareData.status_code = 404
                return exception_response('not_found', {
                    'title': StringStorage.PAGE_NOT_FOUND.value,
                })

            except Exception as e:
                MiddlewareData.status_code = 500
                log_error(module_name=__name__, msg=str(e))
                context = update_context(request=request, title=title, context={
                    'title': StringStorage.SERVER_ERROR.value,
                    'detail': str(e)
                })
                template_name_ = WEB_TEMPLATE_FORMAT.format(os.path.join(WEB_PERMISSIONS_FOLDER_NAME, 'error'))
                return render(request, template_name_, context=context)

        return wrapper

    return inner
