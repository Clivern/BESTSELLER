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
from django.shortcuts import reverse

from app.tests.base import Base


class TestAuthorization(Base, TestCase):
    """TestAuthorization Class"""

    def test_get(self):
        response = self.client.get(reverse("app.web.health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"status": "ok"}')

        content = self.read_file("/storage/logs/prod.log")
        self.assertTrue("Authorize GET Request to /_health" in content and "INFO" in content)
