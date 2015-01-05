class MozillaPasswordsException(Exception):
    """MozillaPasswords Base Exception"""
    pass


class NssLinkingError(MozillaPasswordsException):
    """Indicates a failure to find the NSS library"""
    pass


class NssInitializationError(MozillaPasswordsException):
    """Indicates a failure to initialize the NSS library"""
    pass


class Base64DecodingError(MozillaPasswordsException):
    pass


class PasswordDecryptionError(MozillaPasswordsException):
    pass
