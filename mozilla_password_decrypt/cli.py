# Copyright (C) 2015 Sebastian Pipping <sebastian@pipping.org>
#
# Licensed under MPL 1.1 / GPL 2.0 or later / LGPL 2.1 or later

from __future__ import print_function

import errno
import json
import os
import sqlite3
import sys
from argparse import ArgumentParser
from collections import namedtuple
from glob import glob

from .decrypt import (
    Base64DecodingFailedException, NssInitializationFailedException,
    NssLinkingFailedException, PasswordDecryptionFailedException,
    decrypt_single)


MOZLOGIN = [  # Format of mozilla signons SQLite database
    'id',
    'hostname',
    'httpRealm',
    'formSubmitURL',
    'usernameField',
    'passwordField',
    'encryptedUsername',
    'encryptedPassword',
    'guid',
    'encType',
    'timeCreated',
    'timeLastUsed',
    'timePasswordChanged',
    'timesUsed',
]
MOZLOGIN.extend([  # non-db fields for decrypted values
    'decryptedUsername',
    'decryptedPassword',
])
MozLogin = namedtuple('MozillaLogin', MOZLOGIN)


def main():
    parser = ArgumentParser()
    parser.add_argument('profile_paths', nargs='*', metavar='PATH',
                        help='Profiles to analyze (default: auto detection)')
    options = parser.parse_args()

    if options.profile_paths:
        profiles_to_scan = options.profile_paths
    else:
        profiles_to_scan = []
        for pattern in (
                os.path.expanduser('~/.mozilla/firefox/*.default/'),
                os.path.expanduser('~/.thunderbird/*.default/'),
                ):
            profiles_to_scan += glob(pattern)

    details_of_profile = {}
    d = {
        'version': 3,
        'profiles': details_of_profile,
    }
    success = True

    for profile_path in profiles_to_scan:
        filename = os.path.join(profile_path, 'signons.sqlite')
        if not os.path.exists(filename):
            print('Database file "%s" not found' % filename, file=sys.stderr)
            continue

        try:
            connection = sqlite3.Connection(filename)
        except sqlite3.OperationalError as e:
            print('%s (file "%s")' % (e, filename), file=sys.stderr)
            continue

        details_of_id = {}
        details_of_profile[profile_path] = details_of_id

        cursor = connection.execute('''
            SELECT *
            , "" AS decryptedUsername
            , "" AS decryptedPassword
            FROM moz_logins
            ''')
        for password_entry in map(MozLogin._make, cursor.fetchall()):
            encrypted_encoded = \
                password_entry.encryptedPassword.encode('utf-8')
            decrypted_password = None
            try:
                decrypted_password = \
                    decrypt_single(profile_path, encrypted_encoded)
            except NssInitializationFailedException:
                print('NSS initialization failed for profile path "%s".'
                      % profile_path, file=sys.stderr)
                sys.exit(1)
            except NssLinkingFailedException as e:
                print('Dynamically linking to NSS failed: %s' % e,
                      file=sys.stderr)
                sys.exit(1)
            except Base64DecodingFailedException:
                print('Base64 decoding failed (database "%s", id %d).'
                      % (filename, _id), file=sys.stderr)
                success = False
                continue
            except PasswordDecryptionFailedException:
                print('Password decryption failed (database "%s", id %d).'
                      % (filename, _id), file=sys.stderr)
                success = False
                continue

            if decrypted_password:
                password_entry = password_entry._replace(
                    decryptedPassword=decrypted_password)

            details_of_id[password_entry.id] = password_entry._asdict()

        connection.close()

    if d:
        try:
            json.dump(d, sys.stdout, indent=4, sort_keys=True)
            print()
        except IOError as e:
            if e.errno != errno.EPIPE:  # e.g. when hitting 'q' in less
                raise

    sys.exit(int(not success))
