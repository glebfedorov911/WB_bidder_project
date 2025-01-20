import bcrypt


class PasswordHasher:

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bytes(bcrypt.hashpw(
            password.encode('utf-8'), 
            salt
        ))

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password 
        )