import enum


class StatusEnum(str, enum.Enum):

    QUEUED = "Queued"
    RUNNING = "Running"
    COMPLETED = "Completed"
    ERRORED = "Errored"


    @classmethod
    def from_string(cls, role_str: str):
        try:
            return cls[role_str.upper()]
        except KeyError:
            return None