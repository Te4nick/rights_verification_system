from django.test import TestCase

from access.services.access_service import AccessService


class AccessServiceTest(TestCase):
    def setUp(self) -> None:
        self.service = AccessService()

    def test_add_entry(self):
        pass