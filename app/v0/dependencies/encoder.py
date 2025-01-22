from hashlib import sha256


class Encoder:

    @staticmethod
    def encode(data: str):
        return sha256(data.encode()).hexdigest()

def get_encoder():
    return Encoder()