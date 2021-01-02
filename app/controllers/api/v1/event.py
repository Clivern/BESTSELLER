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
from http import HTTPStatus

from django.views import View
from django.http import HttpResponse
from django.http import JsonResponse

from app.util.validator import Validator
from app.controllers.controller import Controller
from app.service.products_service import ProductsService
from app.exceptions.invalid_request import InvalidRequest


class S3Event(View, Controller):
    """S3 Event Controller

    Attributes:
        validator: an instance of validator class
        products_service: an instance of products service
    """

    def __init__(self):
        self.validator = Validator()
        self.products_service = ProductsService()

    def put(self, request):
        # Validate request data
        result = self.validator.validate(
            request.body.decode('utf-8'),
            self.validator.get_schema_path("/schemas/api/v1/s3/event.json")
        )

        if not result:
            raise InvalidRequest(
                self.validator.get_error(),
                HTTPStatus.BAD_REQUEST
            )

        request_body = json.loads(request.body.decode('utf-8'))
        remote_file = request_body["Records"][0]["s3"]["object"]["key"]

        # Skip if the uploaded file not in the right dir or not XML
        if not self.products_service.is_valid_products_file(remote_file):
            return HttpResponse(status=HTTPStatus.OK)

        # Dispatch a queue task
        task = self.products_service.dispatch_task({
            "remote_file": remote_file
        })

        return JsonResponse(
            {"id": task.uuid, "status": task.status, "createdAt": task.created_at},
            status=HTTPStatus.ACCEPTED
        )
