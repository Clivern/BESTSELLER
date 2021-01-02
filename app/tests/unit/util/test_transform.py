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

from app.tests.base import Base
from app.util.transform import Transform
from app.util.file_system import FileSystem


class TestTransform(Base, TestCase):
    """TestLogger Class"""

    def setUp(self):
        self.transform = Transform()
        self.file_system = FileSystem()

    def test_xml_to_json(self):
        self.file_system.write_file(self.file_system.storage_path("/cache/products_test01.xml"), """
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

        xml = self.file_system.read_file(self.file_system.storage_path("/cache/products_test01.xml"))

        obj = self.transform.xml_to_json(xml)
        self.assertEqual(obj["nsx:items"]["nsx:item"][0]["@id"], "2445456")
        self.assertEqual(obj["nsx:items"]["nsx:item"][1]["@id"], "2445457")
        self.assertEqual(
            self.file_system.storage_path("/cache"),
            self.file_system.storage_path("cache")
        )
