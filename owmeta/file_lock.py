from time import sleep
import os
import errno
import random


class lock_file(object):
    def __init__(self, fname, unique_key=None, wait_interval=.01):
        '''
        Parameters
        ----------
        fname : str
            The lock file
        unique_key : str
            A key for the lock request. This can be ommitted, but in that case, the lock
            will not be tolerant to process failures because you cannot restart a process
            with the same key to release the lock.
        wait_interval : int or float
            How long to wait before
        '''
        if not unique_key:
            self._name = bytes(random.randrange(32, 127) for _ in range(10))
        else:
            self._name = unique_key.decode('UTF-8')

        self.fname = fname
        self.wait_interval = wait_interval

    def __enter__(self):
        self._flocs = []
        self._acq_ll()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def _acq_ll(self):
        have_lock = False
        self.released = False
        while not have_lock:
            try:
                fd = os.open(self.fname, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
                os.write(fd, self._name)
                os.close(fd)
                have_lock = True
            except OSError as oserr:
                if oserr.errno != errno.EEXIST:
                    raise
                try:
                    with open(self.fname) as f:
                        if f.read() == self._name:
                            have_lock_lock = True
                            continue
                except IOError as e:
                    if e.errno != errno.ENOENT:
                        raise
                sleep(self.wait_interval)

    def _rel_ll(self):
        if not self.released:
            os.unlink(self.fname)
            self.released = True

    def release(self):
        self._rel_ll()
