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

from django.test import TestCase
from faker import Faker

from app.tests.base import Base
from app.exceptions.invalid_request import InvalidRequest
from app.exceptions.error_codes import ErrorCodes


class TestInvalidRequest(Base, TestCase):
    """TestInvalidRequest Class"""

    def setUp(self):
        self.fake = Faker()

    def test_get_http_status_and_error_reference(self):
        message = self.fake.sentence(nb_words=5)
        code = self.fake.random_int(min=100, max=1000)
        ref = ErrorCodes.CLIENT_ERROR

        exception = InvalidRequest(message, code, ref)

        self.assertEqual(exception.get_http_status_code(), code)
        self.assertEqual(exception.get_error_code(), ref)
        self.assertTrue(isinstance(exception.get_error_code(), dict))
        self.assertEqual(str(exception), message)
