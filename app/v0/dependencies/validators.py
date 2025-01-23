import re

from core.settings import settings


class Validator:

    def valid(self, data: str):
        raise NotImplementedError("Has Not Method")

class PhoneValidator(Validator):
    PHONE_PATTERN = r"^\+\d{10,15}$"

    def valid(self, phone: str) -> str:
        if not re.match(pattern=self.PHONE_PATTERN, string=phone):
            raise CustomHTTPException("Invalid Phone Format")
        return phone

class EmailValidator(Validator):
    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    def valid(self, email: str) -> str:
        if not re.match(pattern=self.EMAIL_PATTERN, string=email):
            raise CustomHTTPException("Invalid Phone Format")
        return email

def validate_password(value):
    if len(value) < settings.auth.PASSWORD_LENGTH:
        raise ValueError("Password must be at least 8 char long")
    if not any(char.isalpha() for char in value):
        raise ValueError("Password must contain at least one letter")
    if not any(char.isdigit() for char in value):
        raise ValueError("Password must contain at least one digit")
    if not any(char in "!@#$%^&*()-_+=" for char in value):
        raise ValueError("Password must contain at least one special character (!@#$%^&*()-_+=)")
    return value

def get_email_validator():
    return EmailValidator()

def get_phone_validator():
    return PhoneValidator()