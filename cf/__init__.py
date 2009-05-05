# -*- coding: utf-8 -*-

# crunchyfrog - a database schema browser and query tool
# Copyright (C) 2008 Andi Albrecht <albrecht.andi@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""CrunchyFrog Package"""

import gettext
import os
import os.path
import sys
import urlparse


class CFError(Exception):
    """Base class for all errors."""


PREFIX = '/usr/'

def _is_source_dir():
    """Checks if the application is started from source checkout/dist."""
    anchor = os.path.dirname(__file__)
    setup_py = os.path.join(anchor, '../setup.py')
    # Look into setup.py. It's not enough to check for the presence of
    # setup.py. Some modules (e.g. virtualenv) install a setup.py directly
    # in site-packages :-(
    if os.path.exists(setup_py) and 'crunchyfrog' in open(setup_py).read():
        return True
    return False

if _is_source_dir():
    DATA_DIR = os.path.join(os.path.dirname(__file__), '../data/')
    LOCALE_DIR = os.path.join(os.path.dirname(__file__), '../po/')
    MANUAL_URL = os.path.abspath(
        os.path.join(os.path.dirname(__file__),
                     '../docs/manual/build/html/')
        )
else:
    if not os.path.exists(os.path.join(PREFIX, 'share/crunchyfrog')):
        PREFIX = '/usr/local/'
    DATA_DIR = os.path.join(PREFIX, 'share/crunchyfrog/')
    LOCALE_DIR = os.path.join(PREFIX, 'share/locale/')
    MANUAL_URL = '/usr/share/doc/crunchyfrog/manual/'

if not sys.platform.startswith('win'):
    MANUAL_URL = urlparse.urlunsplit(('file', '', MANUAL_URL, '', ''))

DATA_DIR = os.path.abspath(DATA_DIR)
LOCALE_DIR = os.path.abspath(LOCALE_DIR)


PLUGIN_DIR = os.path.join(DATA_DIR, "plugins")
USER_CONFIG_DIR = os.path.abspath(os.path.expanduser("~/.config/crunchyfrog"))
USER_CONF = os.path.join(USER_CONFIG_DIR, "config")
if not os.path.isdir(USER_CONFIG_DIR):
    os.makedirs(USER_CONFIG_DIR)
USER_DIR = os.path.abspath(os.path.expanduser("~/.crunchyfrog"))
if not os.path.isdir(USER_DIR):
    os.makedirs(USER_DIR)
USER_PLUGIN_DIR = os.path.join(USER_DIR, "plugins/")
if not os.path.isdir(USER_PLUGIN_DIR):
    os.makedirs(USER_PLUGIN_DIR)
USER_PLUGIN_REPO = os.path.join(USER_DIR, "repo.xml")
IPC_SOCKET = os.path.join(USER_DIR, "crunchyfog.sock")

gettext.bindtextdomain('crunchyfrog', LOCALE_DIR)
gettext.textdomain('crunchyfrog')
gettext.install('crunchyfrog', LOCALE_DIR, True)

# Add sqlparse to PYTHONPATH
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
