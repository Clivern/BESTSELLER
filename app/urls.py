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

from django.urls import include, path

from app.controllers.web.home import Home
from app.controllers.web.health import Health
from app.controllers.api.v1.event import S3Event
from app.controllers.web.error import handler404 as handler404_view
from app.controllers.web.error import handler500 as handler500_view


urlpatterns = [
    # Guest web pages
    path('', Home.as_view(), name='app.web.home'),
    path('_health', Health.as_view(), name='app.web.health'),

    # v1 API Endpoints
    path('api/v1/', include([
        # Endpoint for S3 bucket events
        path('s3/event', S3Event.as_view(), name='app.api.v1.s3_event.endpoint'),
    ]))
]

handler404 = handler404_view
handler500 = handler500_view
