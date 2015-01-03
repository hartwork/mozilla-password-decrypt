# Copyright (C) 2009 Nelson Bolyard <nelson%bolyard.com>
# Copyright (C) 2015 Sebastian Pipping <sebastian%pipping.org>
#
# Licensed under MPL 1.1/GPL 2.0/LGPL 2.1
#
# This is a port of
#   security/nss/cmd/pwdecrypt/pwdecrypt.c
#   licensed under MPL 1.1/GPL 2.0/LGPL 2.1
#   retrieved from https://github.com/mozilla-services/services-central-legacy/blob/master/security/nss/cmd/pwdecrypt/pwdecrypt.c
#   on 2015-01-02 21:00 UTC+1

from ctypes import c_uint as c_enum
from ctypes import CDLL, POINTER, Structure, byref, c_char_p, c_int, cast, \
    string_at

SECSuccess = 0  # security/nss/lib/util/seccomon.h
siBuffer = 0  # security/nss/lib/util/seccomon.h
PR_TRUE = 1  # nsprpub/pr/include/prtypes.h
PR_FALSE = 0  # nsprpub/pr/include/prtypes.h
PW_NONE = 0  # modules/libmar/sign/nss_secutil.h


class SECItem(Structure):  # security/nss/lib/util/seccomon.h
    _fields_ = [
        ('type', c_enum),
        ('data', c_char_p),
        ('len', c_int),
    ]

class secuPWData(Structure):  # modules/libmar/sign/nss_secutil.h
    _fields_ = [
        ('source', c_enum),
        ('data', c_char_p),
    ]


class MozillaPasswordDecryptException(BaseException):
    pass

class NssInitializationFailedException(MozillaPasswordDecryptException):
    pass

class NssLinkingFailedException(MozillaPasswordDecryptException):
    pass

class Base64DecodingFailedException(MozillaPasswordDecryptException):
    pass

class PasswordDecryptionFailedException(MozillaPasswordDecryptException):
    pass


def decrypt_single(profile_path, encrypted):
    try:
        nss = CDLL('libnss3.so')
    except OSError as e:
        raise NssLinkingFailedException(e)

    rv = nss.NSS_Init(profile_path)
    if rv != SECSuccess:
        raise NssInitializationFailedException()

    try:
        decoded_orig = nss.NSSBase64_DecodeBuffer(None, None, encrypted, len(encrypted))
        if decoded_orig == 0:
            raise Base64DecodingFailedException()

        decoded = cast(decoded_orig, POINTER(SECItem))
        if decoded[0].len == 0:
            raise Base64DecodingFailedException()

        try:
            result = SECItem()
            result.type = siBuffer
            result.data = None
            result.len = 0

            pwdata = secuPWData()
            pwdata.source = PW_NONE
            pwdata.data = None

            rv = nss.PK11SDR_Decrypt(decoded, byref(result), byref(pwdata))
            if rv != SECSuccess:
                raise PasswordDecryptionFailedException()

            decrypted = string_at(result.data, result.len)
            nss.SECITEM_ZfreeItem(byref(result), PR_FALSE)
            return decrypted
        finally:
            nss.SECITEM_ZfreeItem(decoded, PR_TRUE)
    finally:
        nss.NSS_Shutdown()
