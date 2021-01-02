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

import os
import json

from django.test import TestCase
from django.shortcuts import reverse

from app.tests.base import Base
from app.repository.task_repository import TaskRepository


class TestS3Event(Base, TestCase):
    """TestS3Event Class"""

    def setUp(self):
        self.task_repository = TaskRepository()

    def test_event_success(self):
        response = self.client.put(reverse("app.api.v1.s3_event.endpoint"), json.dumps({
                "Records": [
                    {
                        "s3": {
                            "bucket": {
                                "name": os.getenv('AWS_S3_BUCKET_NAME')
                            },
                            "object": {
                                "key": os.getenv('AWS_S3_IMPORT_PATH') + "/product.xml"
                            }
                        }
                    }
                ]
            }), content_type="application/json")

        response_obj = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 202)
        self.assertTrue(response_obj["id"] != "")
        self.assertEqual(response_obj["status"], TaskRepository.PENDING)
        self.assertEqual(self.task_repository.get_one_by_uuid(response_obj["id"]).status, TaskRepository.PENDING)

    def test_event_failure_missing_bucket_name(self):
        response = self.client.put(reverse("app.api.v1.s3_event.endpoint"), json.dumps({
                "Records": [
                    {
                        "s3": {
                            "bucket": {
                                "name": ""
                            },
                            "object": {
                                "key": os.getenv('AWS_S3_IMPORT_PATH') + "/product.xml"
                            }
                        }
                    }
                ]
            }), content_type="application/json")

        self.assertEqual(response.status_code, 400)

    def test_event_failure_missing_file(self):
        response = self.client.put(reverse("app.api.v1.s3_event.endpoint"), json.dumps({
                "Records": [
                    {
                        "s3": {
                            "bucket": {
                                "name": os.getenv('AWS_S3_BUCKET_NAME')
                            },
                            "object": {
                                "key": ""
                            }
                        }
                    }
                ]
            }), content_type="application/json")

        self.assertEqual(response.status_code, 400)
