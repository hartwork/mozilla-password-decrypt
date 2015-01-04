# Copyright (C) 2015 Sebastian Pipping <sebastian@pipping.org>
#
# Licensed under MPL 1.1 / GPL 2.0 or later / LGPL 2.1 or later

from __future__ import print_function

import json
import os
import sqlite3
import sys
from argparse import ArgumentParser
from glob import glob

from .decrypt import Base64DecodingFailedException, \
    NssInitializationFailedException, NssLinkingFailedException, \
    PasswordDecryptionFailedException, decrypt_single


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
        'version': 2,
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

        output = []
        details_of_profile[profile_path] = output

        cursor = connection.execute('SELECT * FROM moz_logins;')
        for row in cursor.fetchall():
            _id, _hostname, _httpRealm, _formSubmitURL, _usernameField, \
                _passwordField, _encryptedUsername, _encryptedPassword, \
                _guid, _encType, _timeCreated, _timeLastUsed, \
                _timePasswordChanged, _timesUsed = \
                row

            entry = {
                'id': _id,
                'hostname': _hostname,
                'httpRealm': _httpRealm,
                'formSubmitURL': _formSubmitURL,
                'usernameField': _usernameField,
                'passwordField': _passwordField,
                'encryptedUsername': _encryptedUsername,
                'encryptedPassword': _encryptedPassword,
                'guid': _guid,
                'encType': _encType,
                'timeCreated': _timeCreated,
                'timeLastUsed': _timeLastUsed,
                'timePasswordChanged': _timePasswordChanged,
                'timesUsed': _timesUsed,
            }
            output.append(entry)

            encrypted_encoded = _encryptedPassword.encode('utf-8')

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

            entry['decryptedPassword'] = decrypted_password

        connection.close()

    if d:
        json.dump(d, sys.stdout, indent=4, sort_keys=True)
        print()

    sys.exit(int(not success))
