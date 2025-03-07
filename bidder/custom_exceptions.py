from enum import Enum


class AlreadyAuthenticatedException(Exception):
    ...

class CPMException(Enum):
    NOT_REGISTER_FABRIC = "This fabric %s not registry"