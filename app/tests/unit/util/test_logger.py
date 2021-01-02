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
from app.util.logger import Logger


class TestLogger(Base, TestCase):
    """TestLogger Class"""

    def setUp(self):
        self.fake = Faker()
        self.logger = Logger().get_logger(__name__)

    def test_info_record_log(self):
        record = self.fake.text(max_nb_chars=20)

        self.logger.info(record)

        content = self.read_file("/storage/logs/prod.log")
        self.assertTrue(record in content and "INFO" in content)

    def test_error_record_log(self):
        record = self.fake.text(max_nb_chars=20)

        self.logger.error(record)

        content = self.read_file("/storage/logs/prod.log")
        self.assertTrue(record in content and "ERROR" in content)

    def test_warn_record_log(self):
        record = self.fake.text(max_nb_chars=20)
        self.logger.warning(record)

        content = self.read_file("/storage/logs/prod.log")
        self.assertTrue(record in content and "WARNING" in content)
