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
import uuid

from faker import Faker
from django.test import TestCase

from app.tests.base import Base
from app.repository.task_repository import TaskRepository


class TestTaskRepository(Base, TestCase):
    """TestTaskRepository Class"""

    def setUp(self):
        self.fake = Faker()
        self.task_repository = TaskRepository()

    def test_insert_one(self):
        task_uuid = str(uuid.uuid4())

        task = self.task_repository.insert_one({
            "uuid": task_uuid,
            "status": TaskRepository.PENDING,
            "payload": "",
            "result": ""
        })

        result = self.task_repository.get_one_by_id(task.id)
        self.assertEqual(result.uuid, task_uuid)

    def test_get_many_by_status(self):
        task_uuid = str(uuid.uuid4())

        self.task_repository.insert_one({
            "uuid": task_uuid,
            "status": TaskRepository.SUCCEEDED,
            "payload": "",
            "result": ""
        })

        result = self.task_repository.get_many_by_status(TaskRepository.SUCCEEDED)
        self.assertEqual(result[0].uuid, task_uuid)

    def test_update_one_by_id(self):
        task = self.task_repository.insert_one({
            "uuid": str(uuid.uuid4()),
            "status": TaskRepository.PENDING,
            "payload": "",
            "result": ""
        })

        result = self.task_repository.get_one_by_id(task.id)
        self.assertEqual(result.status, TaskRepository.PENDING)

        result = self.task_repository.get_one_by_uuid(task.uuid)
        self.assertEqual(result.status, TaskRepository.PENDING)

        self.task_repository.update_one_by_id(task.id, {
            "status": TaskRepository.SUCCEEDED
        })

        # Status changed now
        result = self.task_repository.get_one_by_id(task.id)
        self.assertEqual(result.status, TaskRepository.SUCCEEDED)

    def test_get_many_by_status_and_file(self):
        self.task_repository.insert_one({
            "uuid": str(uuid.uuid4()),
            "status": TaskRepository.PENDING,
            "payload": json.dumps({"remote_file": "partners-files/product9.xml"}),
            "result": ""
        })

        tasks = self.task_repository.get_many_by_status_and_file(TaskRepository.PENDING, "product9.xml")
        self.assertEqual(len(tasks), 1)

        tasks = self.task_repository.get_many_by_status_and_file(TaskRepository.PENDING, "product8.xml")
        self.assertEqual(len(tasks), 0)
