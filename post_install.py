import sys
del sys.path[0] # We want to get the installed PyOpenWorm, not the local one
from setuptools import setup
from subprocess import call
import os, shutil, glob, PyOpenWorm

package_location = PyOpenWorm.__path__[0]
pwd = os.path.dirname(os.path.realpath(__file__))
user_id = os.stat(pwd).st_uid # this is the person that cloned the repo
script_location = os.path.join(pwd, 'OpenWormData', 'scripts')
user_script = 'insert_worm.py' # script(s) we want to be run as non-root

print('Running {}'.format(user_script))
call([sys.executable, user_script], cwd = script_location, preexec_fn=os.setuid(user_id))
# move created database files to your library's package directory
db_files = glob.glob(os.path.join(script_location, 'worm.db*'))
for db_file in db_files:
  print('copying {} to {}'.format(db_file, package_location))
  new_location = os.path.join(package_location, os.path.basename(db_file))
  shutil.copy(db_file, package_location)
  os.chmod(new_location, 0777)
# change directory owner to allow writing and reading from db in that dir
os.chown(package_location, user_id, -1)
