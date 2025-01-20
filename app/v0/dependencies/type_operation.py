from enum import Enum


class TypeOperation(Enum):
    EQUAL = "e"
    GREATER = "gr"
    GREATER_OR_EQUAL = "gre"
    LOWER = "l"
    LOWER_OR_EQUAL = "le"