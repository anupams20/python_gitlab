from abc import ABC, abstractmethod

from pydantic import EmailStr


class EmailProvider(ABC):

    @abstractmethod
    async def send_email(self, recipient: EmailStr, subject: str, body: str):
        pass
