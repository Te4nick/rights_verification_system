import time
from uuid import uuid4

from django.test import TestCase
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from .models import AccessRights, AccessLogStatus, AccessLogEntry
from .services.access_service import AccessService
from .services.log_service import LogService
from .views import AccessViewSet


# Unit Tests
class AccessServiceTest(TestCase):
    def setUp(self) -> None:
        self.service = AccessService()
        self.test_rights = {
            'dev': {
                'log': AccessRights(True, True, True),
                }
        }

    def test_add_entry(self):
        test_table = {
            'input': {
                'user': 'dev',
                'resource': 'log',
                'read': True,
                'write': True,
                'execute': True,
            },
            'result': {
                'rights': self.test_rights
            }
        }
        self.service.add_entry(**test_table['input'])
        self.assertEqual(self.service.rights, test_table['result']['rights'])

    def test_check_access_success(self):
        test_table = {
            'input': {
                'user': 'dev',
                'resource': 'log',
            },
            'result': AccessRights(True, True, True),
        }
        self.service.rights = self.test_rights
        result = self.service.check_access(**test_table['input'])
        self.assertEqual(result, test_table['result'])

    def test_check_access_user_not_found(self):
        test_table = {
            'input': {
                'user': 'tester',
                'resource': 'log',
            },
            'result': AccessLogStatus.USER_NOT_FOUND,
        }
        self.service.rights = self.test_rights
        result = self.service.check_access(**test_table['input'])
        self.assertEqual(result, test_table['result'])

    def test_check_access_resource_not_found(self):
        test_table = {
            'input': {
                'user': 'dev',
                'resource': 'image',
            },
            'result': {
                'status': AccessLogStatus.RESOURCE_NOT_FOUND,
                'forbidden_access': {
                    'dev': [
                        'image',
                    ]
                }
            }
        }
        self.service.rights = self.test_rights
        result = self.service.check_access(**test_table['input'])
        self.assertEqual(result, test_table['result']['status'])
        self.assertEqual(self.service.forbidden_access, test_table['result']['forbidden_access'])

    def test_check_get_forbidden_access_empty(self):
        test_table = {
            'input': {},
            'result': {
                'forbidden_access': {}
            }
        }
        result = self.service.get_forbidden_access(**test_table['input'])
        self.assertEqual(result, test_table['result']['forbidden_access'])
        self.assertEqual(self.service.forbidden_access, test_table['result']['forbidden_access'])

    def test_check_get_forbidden_access_success(self):
        test_table = {
            'input': {
                'forbidden_access': {
                    'dev': [
                        'image',
                    ]
                }
            },
            'result': {
                'forbidden_access': {
                    'dev': [
                        'image',
                    ]
                }
            }
        }
        self.service.forbidden_access = test_table['input']['forbidden_access']
        result = self.service.get_forbidden_access()
        self.assertEqual(result, test_table['result']['forbidden_access'])
        self.assertEqual(self.service.forbidden_access, test_table['result']['forbidden_access'])


class LogServiceTest(TestCase):
    def setUp(self) -> None:
        self.log_file_name = "test_log_service.csv"
        self.service = LogService(log_file_name=self.log_file_name)

    def test_log_service_init_success(self):
        a = AccessLogEntry("", "", "")
        columns = ";".join(a.__dict__.keys()) + "\n"
        with open(self.service.log_file) as csv_file:
            row_names = csv_file.readline()
            self.assertEqual(row_names, columns)

    def test_write_entry_success(self):
        a = AccessLogEntry("dev", "log", "SUCCESS")
        columns = ";".join(a.__dict__.keys()) + "\n"
        self.service.write_entry("dev", "log", AccessLogStatus.SUCCESS)
        with open(self.service.log_file) as csv_file:
            row_names = csv_file.readline()
            log_entry = csv_file.readline()
            self.assertEqual(row_names, columns)
            self.assertEqual(log_entry, str(a)+"\n")

    def test_get_log_file_path_success(self):
        file_path = (settings.STATIC_URL + "log/" + self.log_file_name)[1:]
        self.assertEqual(self.service.get_log_file_path(), file_path)


# Component tests
class DistanceEducationSystemTests(APITestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = APIRequestFactory()

        self.test_data = {
            "user": "dev",
            "resource": "log",
            "read": True,
            "write": True,
            "execute": False
        }

    def test_post_access_success(self):
        request = self.factory.post("/access", self.test_data)
        response = AccessViewSet.as_view({"post": "post_access"})(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, self.test_data)

    def test_post_access_validation_error(self):
        request = self.factory.post("/access", {})
        response = AccessViewSet.as_view({"post": "post_access"})(request)
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_get_access_success(self):
        request = self.factory.post("/access", self.test_data)
        AccessViewSet.as_view({"post": "post_access"})(request)

        desired_response_data = {"read": True, "write": True, "execute": False}
        request = self.factory.get(f"/access?user={self.test_data['user']}&resource={self.test_data['resource']}")
        response = AccessViewSet.as_view({"get": "get_access"})(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, desired_response_data)

    def test_get_access_validation_error(self):
        desired_response_data = {
            "errors": {
                "resource": [
                    "This field is required."
                ]
            }
        }
        request = self.factory.get(f"/access?user={self.test_data['user']}")
        response = AccessViewSet.as_view({"get": "get_access"})(request)

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data, desired_response_data)

    def test_get_access_user_not_found(self):
        nonexistent_user = "nonexistent_user"
        request = self.factory.get(f"/access?user={nonexistent_user}&resource={self.test_data['resource']}")
        response = AccessViewSet.as_view({"get": "get_access"})(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_access_resource_forbidden(self):
        request = self.factory.post("/access", self.test_data)
        AccessViewSet.as_view({"post": "post_access"})(request)

        request = self.factory.get(f"/access?user={self.test_data['user']}&resource={'image'}")
        response = AccessViewSet.as_view({"get": "get_access"})(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_log_file_success(self):

        request = self.factory.get("/log")
        response = AccessViewSet.as_view({"get": "get_log_file"})(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["done"], False)
        self.assertEqual(response.data["result"], None)

    def test_get_log_file_status_success(self):
        desired_response_data = {
            "id": None,
            "done": True,
            "result": {
                "path": "static/log/access.csv"
            },
        }

        request = self.factory.get("/log")
        response = AccessViewSet.as_view({"get": "get_log_file"})(request)
        desired_response_data["id"] = response.data['id']

        time.sleep(1)

        request = self.factory.get(f"/log/status?id={response.data['id']}")
        response = AccessViewSet.as_view({"get": "get_log_file_status"})(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, desired_response_data)

    def test_get_log_file_status_validation_error(self):
        desired_response_data = {
            "errors": {
                "id": [
                    "This field is required."
                ]
            }
        }

        request = self.factory.get("/log/status?cannot=validate")
        response = AccessViewSet.as_view({"get": "get_log_file_status"})(request)

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data, desired_response_data)

    def test_get_log_file_status_not_found(self):
        op_id = uuid4()

        request = self.factory.get(f"/log/status?id={op_id}")
        response = AccessViewSet.as_view({"get": "get_log_file_status"})(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

