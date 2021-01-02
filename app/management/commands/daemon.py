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
import time
import json

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from app.util.logger import Logger
from app.repository.task_repository import TaskRepository
from app.service.products_service import ProductsService


class Command(BaseCommand):
    """Django command that process queued tasks"""

    help = "Process queued tasks"

    def handle(self, *args, **options):
        """Handle the command"""
        self.stdout.write('Starting the queue consumer...')

        self.products_service = ProductsService()
        self.logger = Logger().get_logger(__name__)

        while True:
            # Poll for new files if the feature is enabled
            if os.getenv('ENABLE_AWS_S3_POLLING').lower() == "true":
                self._poll_new_files()

            # Add interval between polling
            time.sleep(2)

            # Run pending tasks
            self._execute_pending_tasks()

    def _poll_new_files(self):
        """Poll new uploaded files and dispatch a queue task"""
        try:
            files = self.products_service.get_pending_files()

            self.logger.info(_("There is {count} files pending on s3 bucket").format(
                count=len(files)-1
            ))

            for file in files:
                if self.products_service.is_valid_products_file(file):
                    self.logger.info(_("dispatch a new task for remote file {file}").format(
                        file=file
                    ))

                    # Dispatch a Task
                    self.products_service.dispatch_task({
                        "remote_file": file
                    })

        except Exception as e:
            self.logger.error(_("Error while polling s3 bucket for new files: {error}").format(
                error=str(e)
            ))

    def _execute_pending_tasks(self):
        """Execute pending queue tasks"""

        pending_tasks = self.products_service.get_pending_tasks()

        for task in pending_tasks:
            try:
                payload = json.loads(task.payload)

                self.logger.info(_("Execute task with uuid {uuid} and payload {payload}").format(
                    uuid=task.uuid,
                    payload=task.payload
                ))

                # Run The Task
                self.products_service.execute_task(payload)

                time.sleep(1)

                # Task succeeded
                self.logger.info(_("Task with uuid {uuid} succeeded").format(
                    uuid=task.uuid
                ))

                self.products_service.update_task(task.id, TaskRepository.SUCCEEDED, "")

            except Exception as e:
                # Task failed
                self.products_service.update_task(task.id, TaskRepository.FAILED, "")
                self.logger.error(_("Error while executing pending task with {uuid}: {error}").format(
                    uuid=task.uuid,
                    error=str(e)
                ))
