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

from app import APP_ROOT


class Base():

    def read_file(self, rel_file_path):
        f = open(APP_ROOT + rel_file_path, "r")
        return f.read()

    def write_file(self, rel_file_path, content):
        f = open(APP_ROOT + rel_file_path, "w")
        f.write(content)
        f.close()
