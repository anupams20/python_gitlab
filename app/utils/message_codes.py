""" Message codes for api responses """
from pydantic import BaseModel


class MessageMeta(BaseModel):
    id: int
    message: str


class MessageCodes:
    # main codes start from 0
    successful_operation = MessageMeta(id=0, message="Successful Operation")
    internal_error = MessageMeta(id=1, message="Internal Error")
    not_found = MessageMeta(id=2, message="Not Found")
    bad_request = MessageMeta(id=3, message="Bad Request")
    input_error = MessageMeta(id=4, message="Input Error")
    operation_failed = MessageMeta(id=5, message="Operation Failed")
    incorrect_email_or_password = MessageMeta(id=6, message="Invalid Email or Password")
    inactive_user = MessageMeta(id=7, message="Inactive User")
    permission_error = MessageMeta(id=8, message="Dont Have Access"),
    invalid_token = MessageMeta(id=9, message="Invalid Token")

    # services code start from 1001
    @staticmethod
    def get_message_names():
        message_names = {}
        for attr, value in vars(MessageCodes).items():
            message_names[value.id] = value.message
        return message_names
