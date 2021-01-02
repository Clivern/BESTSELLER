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

import json
from faker import Faker
from django.test import TestCase

from app.tests.base import Base
from app.util.validator import Validator


class TestValidator(Base, TestCase):
    """TestValidator Class"""

    def setUp(self):
        self.fake = Faker()
        self.validator = Validator()
        self.schema_path = self.validator.get_schema_path("/app/tests/unit/util/test_schema.json")

    def test_validation_success(self):
        data = {
            "firstName": self.fake.first_name(),
            "lastName": self.fake.last_name(),
            "age": self.fake.pyint(min_value=1, max_value=90)
        }

        self.assertTrue(self.validator.validate(data, self.schema_path))
        self.assertEqual(self.validator.get_error(), "")

        self.assertTrue(self.validator.validate(json.dumps(data), self.schema_path))
        self.assertEqual(self.validator.get_error(), "")

    def test_validation_invalid_input_01(self):
        data = {
            "firstName": "",
            "lastName": self.fake.last_name(),
            "age": self.fake.pyint(min_value=1, max_value=90)
        }

        self.assertFalse(self.validator.validate(data, self.schema_path))
        self.assertEqual(self.validator.get_error(), "Invalid field firstName: '' is too short")

        self.assertFalse(self.validator.validate(json.dumps(data), self.schema_path))
        self.assertEqual(self.validator.get_error(), "Invalid field firstName: '' is too short")

    def test_validation_invalid_input_02(self):
        data = {
            "firstName": self.fake.first_name(),
            "lastName": "",
            "age": self.fake.pyint(min_value=1, max_value=90)
        }

        self.assertFalse(self.validator.validate(data, self.schema_path))
        self.assertEqual(self.validator.get_error(), "Invalid field lastName: '' is too short")

        self.assertFalse(self.validator.validate(json.dumps(data), self.schema_path))
        self.assertEqual(self.validator.get_error(), "Invalid field lastName: '' is too short")

    def test_validation_invalid_input_03(self):
        age = self.fake.pyint(min_value=-90, max_value=0)

        data = {
            "firstName": self.fake.first_name(),
            "lastName": self.fake.last_name(),
            "age": age
        }

        self.assertFalse(self.validator.validate(data, self.schema_path))
        self.assertEqual(
            self.validator.get_error(),
            "Invalid field age: {0} is less than the minimum of 1".format(age)
        )

        self.assertFalse(self.validator.validate(json.dumps(data), self.schema_path))
        self.assertEqual(
            self.validator.get_error(),
            "Invalid field age: {0} is less than the minimum of 1".format(age)
        )

    def test_validation_invalid_data(self):
        data = '"firstName":"something"}'

        self.assertFalse(self.validator.validate(data, self.schema_path))
        self.assertEqual(self.validator.get_error(), "Invalid request data")
