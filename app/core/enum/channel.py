import enum


class ChannelEnum(str, enum.Enum):
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    INSTAGRAM = "instagram"
    WECHAT = "wechat"
    WEBLINK = "weblink"

    @classmethod
    def from_string(cls, role_str: str):
        try:
            return cls[role_str.upper()]
        except KeyError:
            return None
