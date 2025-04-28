import enum


class NotificationStatusEnum(str, enum.Enum):
    QUEUED = "Queued"
    SENT = "Sent"
    FAILED = "Failed"

    @classmethod
    def from_string(cls, role_str: str):
        try:
            return cls[role_str.upper()]
        except KeyError:
            return None
