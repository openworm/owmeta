from __future__ import absolute_import
from __future__ import print_function
import os
import sys
from sysconfig import get_path
from glob import glob
from pkgutil import get_loader


def get_library_location(package):
    # get abs path of a package in the library, rather than locally
    library_package_paths = glob(os.path.join(get_path('platlib'), '*'))
    sys.path = library_package_paths + sys.path
    package_path = os.path.dirname(get_loader(package).get_filename())
    sys.path = sys.path[len(library_package_paths):]
    return package_path
