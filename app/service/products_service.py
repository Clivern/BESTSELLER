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
import uuid
import json

import boto3
from botocore.exceptions import ClientError
from django.utils.translation import gettext as _

from app.util.logger import Logger
from app.util.transform import Transform
from app.util.file_system import FileSystem
from app.repository.task_repository import TaskRepository


class ProductsService():
    """ProductsService Class

    Attributes:
        task_repository: an instance of task repository
        transform: an instance of transform data types util class
        file_system: an instance file system util class
        logger: an instance of logger
        s3_client: an instance of s3 client
    """

    def __init__(self):
        """Inits PartnerProductsService"""
        self.task_repository = TaskRepository()
        self.transform = Transform()
        self.file_system = FileSystem()
        self.logger = Logger().get_logger(__name__)
        session = boto3.session.Session()
        self.s3_client = session.client(
            's3',
            region_name=os.getenv('AWS_S3_REGION_NAME'),
            endpoint_url=os.getenv('AWS_S3_ENDPOINT_URL'),
            aws_access_key_id=os.getenv('AWS_S3_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_S3_SECRET_KEY')
        )

    def execute_task(self, payload):
        """Execute pending tasks

        Args:
            payload: a task payload, for example {"remote_file": "s3 remote path"}
        """
        local_path = self.file_system.storage_path("/cache/" + os.path.basename(payload["remote_file"]))
        new_file = self.file_system.storage_path("/cache/" + os.path.basename(payload["remote_file"]).replace(".xml", ".json"))

        try:
            # Download xml file to cache dir
            self.s3_client.download_file(
                os.getenv('AWS_S3_BUCKET_NAME'),
                payload["remote_file"],
                local_path,
            )
        except ClientError as e:
            self.logger.warning(_("Client error while downloading file {file}: {error}").format(
                file=payload["remote_file"],
                error=str(e)
            ))

        # Convert XML file to JSON file
        self._transform_products_format(local_path, new_file)

        # Upload the json file to s3 bucket path
        self.s3_client.upload_file(
            Bucket=os.getenv('AWS_S3_BUCKET_NAME'),
            Filename=new_file,
            Key=os.path.join(os.getenv('AWS_S3_OUTPUT_PATH'), os.path.basename(new_file))
        )

        # Delete the xml file from s3 bucket
        self.s3_client.delete_object(
            Bucket=os.getenv('AWS_S3_BUCKET_NAME'),
            Key=os.path.join(os.getenv('AWS_S3_IMPORT_PATH'), os.path.basename(payload["remote_file"]))
        )

        # Delete local files inside the cache dir
        self.file_system.delete_file(local_path)
        self.file_system.delete_file(new_file)

    def dispatch_task(self, data):
        """ Store a new task in database to be picked by queue consumer

        Args:
            data: the task data. for example {"remote_file": "..."}

        Returns:
            An instance of the created task
        """

        # Get Pending tasks for the provided file
        # To Avoid duplicate tasks from the endpoint and the polling daemon
        pending_tasks = self.task_repository.get_many_by_status_and_file(
            TaskRepository.PENDING,
            data["remote_file"]
        )

        if len(pending_tasks) > 0:
            return False

        return self.task_repository.insert_one({
            "uuid": str(uuid.uuid4()),
            "status": TaskRepository.PENDING,
            "payload": json.dumps(data),
            "result": json.dumps({})
        })

    def get_pending_tasks(self):
        """Get pending tasks from database

        Returns:
            A list of pending tasks
        """
        return self.task_repository.get_many_by_status(TaskRepository.PENDING)

    def update_task(self, id, status, result):
        """Update task status and result

        Args:
            id: the task id.
            status: the task status
            result: the task result after execution

        Returns:
            A boolean representing the success of the operation
        """
        return self.task_repository.update_one_by_id(id, {
            "status": status,
            "result": result
        })

    def get_pending_files(self):
        """Gets the pending files from S3 bucket path

        Returns:
            A list of file paths
        """
        response = self.s3_client.list_objects(
            Bucket=os.getenv('AWS_S3_BUCKET_NAME'),
            Prefix=os.getenv('AWS_S3_IMPORT_PATH')
        )

        files = []
        for obj in response['Contents']:
            files.append(obj['Key'])

        return files

    def _transform_products_format(self, xml_file_path, json_file_path):
        """Transform products XML file into JSON file

        Args:
            xml_file_path: The input XML file path
            json_file_path: The output JSON file path
        """
        i = 0
        new_data = []
        xml_content = self.file_system.read_file(xml_file_path)
        data_obj = self.transform.xml_to_json(xml_content)

        for nsx_item in data_obj["nsx:items"]["nsx:item"]:
            new_data.append({})
            new_data[i]["product_id"] = nsx_item["@id"]
            new_data[i]["product_category"] = nsx_item["nsx:category"]
            new_data[i]["product_description"] = nsx_item["nsx:description"]
            new_data[i]["product_images"] = {}
            new_data[i]["prices"] = []

            j = 1
            for nsx_item_image in nsx_item["nsx:images"]["nsx:image"]:
                while nsx_item_image["@type"] != str(j):
                    new_data[i]["product_images"]["image_" + str(j)] = None
                    j += 1

                new_data[i]["product_images"]["image_" + nsx_item_image["@type"]] = nsx_item_image["@url"]
                j += 1

            for nsx_item_price in nsx_item["nsx:prices"]["nsx:price"]:
                new_data[i]["prices"].append({
                    "currency": nsx_item_price["nsx:currency"],
                    "value": nsx_item_price["nsx:value"]
                })
            i += 1

        # Store the JSON file with JSON data
        self.file_system.write_file(
            json_file_path,
            json.dumps(new_data)
        )

    def is_valid_products_file(self, file_key):
        """Validate if the S3 event file is a valid XML file

        Args:
            file_key: S3 file key

        Returns:
            A boolean representing that the file is XML and on the right import path
        """

        return file_key.endswith(".xml") and file_key.startswith(os.getenv('AWS_S3_IMPORT_PATH'))
