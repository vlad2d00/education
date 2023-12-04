from rest_framework.request import Request


def get_request_ip_address(request: Request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_request_user_agent(request: Request) -> str:
    return request.META["HTTP_USER_AGENT"]


def get_request_host(request: Request) -> str:
    return request.META["HTTP_HOST"]


def get_request_referer(request: Request) -> str:
    return request.META.get('HTTP_REFERER')
