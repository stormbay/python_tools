import os
import platform
import sys
import string
import re


def get_system_type():
    """Returns a "normalized" version of platform.system (transforming CYGWIN
    to Windows, for example).

    Returns None if not a supported platform.

    """
    plat = platform.system()
    if plat == 'Windows':
        return 'Windows'
    if re.search('CYGWIN', plat) is not None:
        # On certain installs, the default windows shell
        # runs cygwin. Treat cygwin as windows for this
        # purpose
        return 'Windows'
    if plat == 'Linux':
        return 'Linux'
    if plat == 'Darwin':
        return 'Darwin'

