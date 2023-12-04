import json
import traceback

from api.db.config import PRINT_DB_LOGS
from api.db.dao import get_or_create_request_method, get_or_create_ip_address, get_or_create_user_agent, \
    mark_ip_address_activity, mark_user_activity
from api.models import Log
from education.handlers import send_error
from education.utils.request_service import get_request_ip_address, get_request_user_agent
from education.utils.datetime_service import datetime_to_string, datetime_timezone_now

FORBIDDEN_PARAMS = ('password', 'repeat_password', 'csrfmiddlewaretoken')


def create_log(request, status_code: int):
    mark_ip_address_activity(request)
    mark_user_activity(request)

    ip_address = get_request_ip_address(request)
    user_agent = get_request_user_agent(request)
    if request.user:
        user_id = request.user.id if not request.user.is_anonymous else None
    else:
        user_id = None

    params = {}
    for key in request.GET.keys():
        if key not in FORBIDDEN_PARAMS:
            params[key] = request.GET[key]
    for key in request.POST.keys():
        if key not in FORBIDDEN_PARAMS:
            params[key] = request.POST[key]

    log = Log.objects.create(path=request.path,
                             kwargs=json.dumps(params) if params else None,
                             status_code=status_code,
                             method_id=get_or_create_request_method(request.method).id,
                             ip_address_id=get_or_create_ip_address(ip_address).id if ip_address else None,
                             user_agent_id=get_or_create_user_agent(user_agent).id if user_agent else None,
                             user_id=user_id)

    if PRINT_DB_LOGS:
        print(str(log))


def log_error(module_name: str, msg: str):
    with open('error.log', 'a') as file:
        dt = datetime_to_string(datetime_timezone_now(), sep_ms=',', accuracy=3)
        file.write(f'{dt} {module_name} ERROR {msg}\n')
        traceback.print_exc(file=file)

    traceback.print_exc()
    send_error(msg)
