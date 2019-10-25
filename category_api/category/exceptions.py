from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.encoding import force_text


class ConflictValidationError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'The category with this name already exists in database. You can update existing category via PUT/PATCH queries'

    def __init__(self, detail, field, status_code):
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = {field: force_text(detail)}
        else: 
            self.detail = {'detail': force_text(self.default_detail)}
