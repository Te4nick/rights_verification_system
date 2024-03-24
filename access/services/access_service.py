from ..models import AccessRights, AccessLogEntry, AccessLogStatus


class AccessService:

    def __init__(self):
        self.rights: dict[str: dict[str: AccessRights]] = {}
        self.forbidden_access: dict[str: list[str]] = {}

    def add_entry(
            self,
            user: str,
            resource: str,
            read: bool = False,
            write: bool = False,
            execute: bool = False
    ) -> None:

        entry = AccessRights(
            is_read=read,
            is_write=write,
            is_exec=execute
        )
        if user not in self.rights:
            self.rights[user] = {}
        self.rights[user][resource] = entry

    def check_access(self, user: str, resource: str) -> AccessRights | AccessLogStatus:

        user_rights = self.rights.get(user)
        if user_rights is None:
            status = AccessLogStatus.USER_NOT_FOUND
            return status

        resource_rights = user_rights.get(resource)
        if resource_rights is None:
            status = AccessLogStatus.RESOURCE_NOT_FOUND
            if user not in self.forbidden_access:
                self.forbidden_access[user] = []
            self.forbidden_access[user].append(resource)
            return status

        return resource_rights

    def get_forbidden_access(self) -> dict[str, list[str]]:
        return self.forbidden_access
