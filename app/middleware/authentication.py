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

from django.utils.translation import gettext as _

from app.util.logger import Logger


class Authentication():
    """
    Authentication Middleware

    This functionality is not implements but only to demonstrate the application architecture

    Attributes:
        get_response: a callable function
        logger: An instance of Logger class
    """

    def __init__(self, get_response):
        """Inits Authentication"""
        self.get_response = get_response
        self.logger = Logger().get_logger(__name__)

    def __call__(self, request):
        """Execute Middleware

        Args:
            request: request instance
        """
        self.logger.info(_("Authenticate {method} Request to {path}").format(
            method=request.method,
            path=request.path
        ))

        response = self.get_response(request)

        return response
