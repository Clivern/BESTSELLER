# Copyright 2021 Clivern
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from http import HTTPStatus

from django.http import JsonResponse
from django.utils.translation import gettext as _

from app.exceptions.error_codes import ErrorCodes
from app.util.logger import Logger


def handler404(request, exception=None, template_name="templates/guest/404.html"):
    """404 Error Page"""

    logger = Logger().get_logger(__name__)

    if exception is not None:
        # Log exceptions only on debug mode
        logger.debug("Route Not Found: {exception}".format(
            exception=exception
        ))

    return JsonResponse({
        'errorCode': ErrorCodes.SERVER_ERROR["code"],
        'errorMessage': _("Page Not Found!"),
        'correlationId': request.META["X-Correlation-ID"],
        'reference': ErrorCodes.SERVER_ERROR["reference"]
    }, status=HTTPStatus.NOT_FOUND)


def handler500(request, exception=None, template_name="templates/guest/500.html"):
    """500 Error Page"""

    logger = Logger().get_logger(__name__)

    if exception is not None:
        logger.error("Internal Server Error: {exception}".format(
            exception=exception
        ))

    return JsonResponse({
        'errorCode': ErrorCodes.SERVER_ERROR["code"],
        'errorMessage': _("Something goes wrong! Please contact a system administrator."),
        'correlationId': request.META["X-Correlation-ID"],
        'reference': ErrorCodes.SERVER_ERROR["reference"]
    }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def csrf_failure(request, reason=""):

    return JsonResponse({
        "error": _("Error! Access forbidden due to invalid CSRF token.")
    })
