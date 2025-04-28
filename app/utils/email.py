from app.notification.email import EmailProvider


class EmailService:
    def __init__(self, provider: EmailProvider):
        self.provider = provider

    async def send_email(self, recipient: str, subject: str, body: str):
        await self.provider.send_email(recipient, subject, body)
