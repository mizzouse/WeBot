# Enumerators and Error Code Types

from enum import Enum

class Login(Enum):
    """Represents our login, logout,
    and any error codes
    """
    default = 0
    Failed = 1
    Success = 2
    LoggedIn = 3
    LoggedOut = 4

