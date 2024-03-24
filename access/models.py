from django.db import models
import enum


class AccessType(enum.Enum):
    read = "read"
    write = "write"
    execute = "execute"


class AccessRights:
    def __init__(self, is_read: bool = False, is_write: bool = False, is_exec: bool = False):
        self.read = is_read
        self.write = is_write
        self.execute = is_exec

    def modify(self, is_read: bool = False, is_write: bool = False, is_exec: bool = False):
        self.read = is_read
        self.write = is_write
        self.execute = is_exec

    def get_rights(self):
        return self.read, self.write, self.execute


class AccessLogStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"


class AccessLogEntry:
    def __init__(self, user: str, resource: str, status: str):
        self.user = user
        self.resource = resource
        self.status = status

    def __repr__(self) -> str:
        return f"{self.user};{self.resource};{self.status}"
