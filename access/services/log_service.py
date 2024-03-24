import os

from rights_verification_system.settings import STATIC_URL
from ..models import AccessLogEntry, AccessLogStatus


class LogService:
    def __init__(self, log_file_name: str = "access.csv", output_log_path: str = STATIC_URL + "log/"):
        self.log_file_name = log_file_name
        self.output_log_path = output_log_path + (
            "/" if output_log_path[-1] != "/" else ""
        )
        self.log_file = output_log_path + log_file_name

        with open(self.log_file, "w") as log_file:
            a = AccessLogEntry("", "", "")
            log_file.write(";".join(a.__dict__.keys()) + "\n")

    def write_entry(self, user: str, resource: str, status: AccessLogStatus) -> None:
        with open(self.log_file, "a") as log_file:
            log_file.write(str(AccessLogEntry(user=user, resource=resource, status=status.value)) + "\n")

    def get_log_file_path(self) -> str:
        return self.log_file
