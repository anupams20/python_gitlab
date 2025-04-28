import enum


class RoleEnum(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    ORG_USER = "org_user"
    GUEST = "guest"

    @classmethod
    def from_string(cls, role_str: str):
        try:
            return cls[role_str.upper()]
        except KeyError:
            return None
