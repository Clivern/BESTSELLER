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
import datetime
import os

import botocore.session
from botocore.stub import Stubber
from django.test import TestCase

from app.tests.base import Base
from app.util.file_system import FileSystem
from app.service.products_service import ProductsService
from app.repository.task_repository import TaskRepository


class TestProductsService(Base, TestCase):
    """TestProductsService Class"""

    def setUp(self):
        self.file_system = FileSystem()
        self.products_service = ProductsService()

    def test_transform_products_format(self):
        self.file_system.write_file(self.file_system.storage_path("/cache/products_test02.xml"), """
        <nsx:items>
            <nsx:item id="2445456">
                <nsx:category>Jeans</nsx:category>
                <nsx:description>Bootleg Front Washed</nsx:description>
                <nsx:images>
                    <nsx:image type="1" url="https://sample.com/img/2445456_Image_1.jpg"/>
                    <nsx:image type="3" url="https://sample.com/img/2445456_Image_3.jpg"/>
                </nsx:images>
                <nsx:prices>
                    <nsx:price>
                        <nsx:currency>EUR</nsx:currency>
                        <nsx:value>49.95</nsx:value>
                    </nsx:price>
                    <nsx:price>
                        <nsx:currency>DKK</nsx:currency>
                        <nsx:value>445.60</nsx:value>
                    </nsx:price>
                </nsx:prices>
            </nsx:item>
            <nsx:item id="2445457">
                <nsx:category>Jeans</nsx:category>
                <nsx:description>Bootleg Front Washed</nsx:description>
                <nsx:images>
                    <nsx:image type="1" url="https://sample.com/img/2445456_Image_1.jpg"/>
                    <nsx:image type="3" url="https://sample.com/img/2445456_Image_3.jpg"/>
                </nsx:images>
                <nsx:prices>
                    <nsx:price>
                        <nsx:currency>EUR</nsx:currency>
                        <nsx:value>49.95</nsx:value>
                    </nsx:price>
                    <nsx:price>
                        <nsx:currency>DKK</nsx:currency>
                        <nsx:value>445.60</nsx:value>
                    </nsx:price>
                </nsx:prices>
            </nsx:item>
        </nsx:items>
        """)

        self.products_service._transform_products_format(
            self.file_system.storage_path("/cache/products_test02.xml"),
            self.file_system.storage_path("/cache/products_test02.json")
        )

        json_content = self.file_system.read_file(self.file_system.storage_path("/cache/products_test02.json"))

        obj = json.loads(json_content)

        self.assertEqual(obj[0]["product_id"], "2445456")
        self.assertEqual(obj[1]["product_id"], "2445457")

        self.file_system.delete_file(self.file_system.storage_path("/cache/products_test02.xml"))
        self.file_system.delete_file(self.file_system.storage_path("/cache/products_test02.json"))

    def test_get_pending_tasks(self):
        result = self.products_service.dispatch_task({"remote_file": "path/product.xml"})
        self.assertTrue(result.id != "")
        self.assertTrue(result.uuid != "")

        pending_tasks = self.products_service.get_pending_tasks()
        self.assertEqual(pending_tasks[0].status, TaskRepository.PENDING)

    def test_dispatch_task(self):
        result = self.products_service.dispatch_task({"remote_file": "path/product.xml"})
        self.assertTrue(result.id != "")
        self.assertTrue(result.uuid != "")
        self.assertEqual(result.status, TaskRepository.PENDING)

    def test_update_task(self):
        result = self.products_service.dispatch_task({"remote_file": "path/product.xml"})
        pending_tasks = self.products_service.get_pending_tasks()
        self.assertEqual(len(pending_tasks), 1)

        self.assertTrue(self.products_service.update_task(result.id, TaskRepository.SUCCEEDED, ""))
        pending_tasks = self.products_service.get_pending_tasks()
        self.assertEqual(len(pending_tasks), 0)

    def test_get_pending_files(self):
        s3 = botocore.session.get_session().create_client('s3')
        stubber = Stubber(s3)

        response = {
            'IsTruncated': False,
            'Name': 'test-bucket',
            'MaxKeys': 1000,
            'Prefix': os.getenv('AWS_S3_IMPORT_PATH'),
            'Contents': [{
                'Key': "products.xml",
                'ETag': '"abc123"',
                'StorageClass': 'STANDARD',
                'LastModified': datetime.datetime(2016, 1, 20, 22, 9),
                'Owner': {'ID': 'abc123', 'DisplayName': 'myname'},
                'Size': 14814
            }],
            'EncodingType': 'url',
            'ResponseMetadata': {
                'RequestId': 'abc123',
                'HTTPStatusCode': 200,
                'HostId': 'abc123'
            },
            'Marker': ''
        }

        expected_params = {
            'Bucket': os.getenv('AWS_S3_BUCKET_NAME'),
            'Prefix': os.getenv('AWS_S3_IMPORT_PATH')
        }

        stubber.add_response('list_objects', response, expected_params)
        stubber.activate()
        self.products_service.s3_client = s3
        self.assertEqual(self.products_service.get_pending_files(), ['products.xml'])

    def test_execute_task(self):
        pass
