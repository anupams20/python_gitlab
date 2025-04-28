from typing import Optional

from mailjet_rest import Client
from pydantic import EmailStr

from app.core.config import settings
from app.core.logging import AppLogger
from app.exceptions import ApplicationException
from app.notification.email import EmailProvider

logger = AppLogger().get_logger()


class MailjetProvider(EmailProvider):
    mailjet_client = None
    sender_email = None

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 sender_email: Optional[EmailStr] = None):
        if api_key is None and settings.MAILJET_API_KEY is None:
            raise ValueError("Either of api_key or MAILJET_API_KEY is not set")
        else:
            api_key = api_key if api_key else settings.MAILJET_API_KEY
        if api_secret is None and settings.MAILJET_API_SECRET is None:
            raise ValueError("Either of api_secret or MAILJET_API_SECRET is not set")
        else:
            api_secret = api_secret if api_secret else settings.MAILJET_API_SECRET
        if sender_email is None and settings.SENDER_EMAIL is None:
            raise ValueError("Either of sender_email or SENDER_EMAIL is not set")
        else:
            sender_email = sender_email if sender_email else settings.SENDER_EMAIL
        self.mailjet_client = Client(auth=(api_key, api_secret), version='v3.1')
        self.sender_email = sender_email

    async def send_email(self, recipient: EmailStr, subject: str, body: str):

        data = {'Messages': [{"From": {"Email": self.sender_email, "Name": "Your Company"},
                              "To": [{"Email": recipient, "Name": "Recipient"}], "Subject": subject, "HTMLPart": body}]}

        result = self.mailjet_client.send.create(data=data)
        if result.status_code == 200:
            logger.info(f"Email sent to {recipient}")
        else:
            logger.error(f"Failed to send email: {result.status_code}, {result.json()}")
            raise ApplicationException(message=f"Unable to send email: {result}")
