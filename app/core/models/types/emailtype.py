from sqlalchemy.types import TypeDecorator, String

import re


class EmailType(TypeDecorator):
    impl = String

    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    def process_bind_param(self, value, dialect):
        return self.__check_valid_email(value)

    def __check_valid_email(self, value):
        if value is not None and not re.match(self.EMAIL_PATTERN, value):
            raise ValueError("Invalid email address")
        return value
            
    def process_result_value(self, value, dialect):
        return value