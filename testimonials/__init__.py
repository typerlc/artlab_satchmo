__docformat__="restructuredtext"

VERSION = (0, 1, 0)

# Dynamically calculate the version based on VERSION tuple
if len(VERSION)>2 and VERSION[2] is not None:
    str_version = "%d.%d-%s" % VERSION[:3]
else:
    str_version = "%d.%d" % VERSION[:2]

__version__ = str_version
