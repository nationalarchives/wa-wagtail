import logging
from http import HTTPStatus

from django.http import HttpResponse
from django.shortcuts import render
from django.views import defaults

logger = logging.getLogger(__name__)


def page_not_found(request, exception, template_name="pages/errors/404.html"):
    return defaults.page_not_found(request, exception, template_name)


def server_error(request, template_name="pages/errors/500.html"):
    return defaults.server_error(request, template_name)


def csrf_failure(
    request,
    reason: str = "",  # given by Django
    template_name: str = "pages/errors/403.html",
):
    csrf_logger = logging.getLogger("django.security.csrf")
    csrf_logger.exception("CSRF Failure: %s", reason)

    return render(request, template_name, status=HTTPStatus.FORBIDDEN)


class HttpResponseUnauthorized(HttpResponse):
    status_code = HTTPStatus.UNAUTHORIZED
