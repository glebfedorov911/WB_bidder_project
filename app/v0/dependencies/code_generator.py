import secrets
import string


class CodeGenerator:
    
    @staticmethod
    def generate_code(length: int = 6) -> str:
        return ''.join([
            secrets.choice(string.digits) for _ in range(length)
        ])