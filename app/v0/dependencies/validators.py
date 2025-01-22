import re


class Validator:

    def valid(self, data: str):
        raise NotImplementedError("Has Not Method")

class PhoneValidator(Validator):
    PHONE_PATTERN = "^\+\d{10,15}$"

    def valid(self, phone: str) -> str:
        if not re.match(pattern=self.PHONE_PATTERN, string=phone):
            raise ValueError("Invalid Phone Format")
        return phone

class EmailValidator(Validator):
    EMAIL_PATTERN = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    def valid(self, email: str) -> str:
        if not re.match(pattern=self.EMAIL_PATTERN, string=email):
            raise ValueError("Invalid Phone Format")
        return email

def get_email_validator():
    return EmailValidator()

def get_phone_validator():
    return PhoneValidator()