import enum


class NotificationTypeEnum(str, enum.Enum):
    EMAIL = "email"

    @classmethod
    def from_string(cls, role_str: str):
        try:
            return cls[role_str.upper()]
        except KeyError:
            return None
