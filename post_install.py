import os, shutil, glob, sys
from sysconfig import get_path
from glob import glob
from pkgutil import get_loader
from setuptools import setup
from subprocess import call

def get_library_location(package):
    # get abs path of a package in the library, rather than locally
    library_package_paths = glob(os.path.join(get_path('platlib'), '*'))
    sys.path = library_package_paths + sys.path
    package_path = get_loader(package).filename
    sys.path = sys.path[len(library_package_paths):]
    return package_path

package_location = get_library_location('PyOpenWorm')
pwd = os.path.dirname(os.path.realpath(__file__))
user_id = os.stat(pwd).st_uid # this is the person that cloned the repo
script_location = os.path.join(pwd, 'OpenWormData', 'scripts')
user_script = 'insert_worm.py' # script(s) we want to be run as non-root

print('Running {} as UID {}'.format(user_script, user_id))
pid = os.fork()
if pid == 0:
    #child process
    try:
        os.seteuid(user_id)
        process = call([sys.executable, user_script], cwd = script_location)
    finally:
        os._exit(0)
os.waitpid(pid, 0)
# move created database files to your library's package directory
db_files = glob(os.path.join(script_location, 'worm.db*'))
for db_file in db_files:
    print('copying {} to {}'.format(db_file, package_location))
    new_location = os.path.join(package_location, os.path.basename(db_file))
    shutil.copy(db_file, package_location)
    os.chmod(new_location, 0777)
# change directory owner to allow writing and reading from db in that dir
os.chown(package_location, user_id, -1)

