from setuptools import setup
from subprocess import call
import os, sys, shutil, glob

# remove current dir from path for this script, since we want to find
# newly installed PyOpenWorm module
del sys.path[0]

import PyOpenWorm

package_location = PyOpenWorm.__path__[0]
pwd = os.path.dirname(os.path.realpath(__file__))
script_location = os.path.join(pwd, 'OpenWormData', 'scripts')
call([sys.executable, 'insert_worm.py'], cwd = script_location)
# move created database files to your library's package directory
db_files = glob.glob(os.path.join(script_location, 'worm.db*'))
for db_file in db_files:
  print('copying {} to {}'.format(db_file, package_location))
  new_location = os.path.join(package_location, os.path.basename(db_file))
  shutil.copy(db_file, package_location)
  os.chmod(new_location, 0777)
# change directory owner to allow writing and reading from db in that dir
os.chown(package_location, os.stat(pwd).st_uid, -1)
