# Copyright (C) 2015 "nyov" <nyov@nexnode.net>
#
# Licensed under MPL 1.1 / GPL 2.0 or later / LGPL 2.1 or later

from os.path import dirname, join
from setuptools import find_packages, setup


description = 'Mozilla password decryptor'
long_description = description
with open(join(dirname(__file__), 'mozilla_password_decrypt/VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()

setup_args = {
    'name': 'mozilla-password-decrypt',
    'version': version,
    'url': 'https://github.com/hartwork/mozilla-password-decrypt',
    'description': description,
    'long_description': long_description,
    'keywords': 'mozilla passwords signons sqlite libnss3',
    'author': 'mozilla-passwords developers',
    'maintainer': 'Sebastian Pipping',
    'maintainer_email': 'sebastian@pipping.org',
    'license': 'MPL 1.1/GPL 2.0/LGPL 2.1',
    'packages': find_packages(),
    'include_package_data': True,
    'zip_safe': False,  # for setuptools
    'entry_points': {
        'console_scripts': [
            'mozilla-password-decrypt = mozilla_password_decrypt:main'
        ],
    },
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: C',
        'Topic :: Database',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Recovery Tools',
    ],
    'install_requires': [
    ],
}

try:
    from local_setup import local_setup_args
    setup_args.update(local_setup_args)
except ImportError:
    pass

setup(**setup_args)
