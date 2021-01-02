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

from django.views import View
from django.shortcuts import render

from app.controllers.controller import Controller


class Home(View, Controller):
    """Home Page Controller"""

    template_name = 'templates/guest/home.html'

    def get(self, request):
        return render(request, self.template_name, {
            "title": os.getenv("APP_NAME", "Bestseller"),
            "description": os.getenv("APP_DESCRIPTION", ""),
            "base_url": os.getenv("APP_URL", ""),
        })
