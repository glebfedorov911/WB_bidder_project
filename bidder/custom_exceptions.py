from enum import Enum


class AlreadyAuthenticatedException(Exception):
    ...

class CPMException(Enum):
    NOT_REGISTER_FABRIC = "This fabric %s not registry"

class WBException(Enum):
    INVALID_REQUEST = "Invalid request, cannot get/change data"