# Copyright (C) 2015 "nyov" <nyov@nexnode.net>
#
# Licensed under MPL 1.1 / GPL 2.0 or later / LGPL 2.1 or later

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
