from queue import Empty
from multiprocessing import Process, Queue, Semaphore
from owmeta.file_lock import lock_file
from os import getpid, makedirs, unlink
from os.path import join as p
from tempfile import TemporaryDirectory

import pytest


def mutex_test_f(v, parent_q, fname, done, wait):
    with lock_file(fname):
        parent_q.put(v, True)
        done.release()
        wait.acquire()


@pytest.mark.inttest
def test_mutex():
    with TemporaryDirectory() as td:
        q = Queue()
        done = Semaphore(0)
        wait = Semaphore(0)
        p1 = Process(target=mutex_test_f, args=(1, q, p(td, 'lockfile'), done, wait))
        p2 = Process(target=mutex_test_f, args=(2, q, p(td, 'lockfile'), done, wait))
        p1.start()
        p2.start()
        done.acquire()
        done.release()
        try:
            print(q.get(timeout=1))
            with pytest.raises(Empty):
                print(q.get(timeout=1))
        finally:
            wait.release()
            wait.release()
            p1.join()
            p2.join()


@pytest.mark.inttest
def test_remove_lock_file():
    '''
    Unlinking the lock file early is not allowed generally and probably indicates a logic
    error, so we give an exception in that case
    '''
    with pytest.raises(OSError):
        with TemporaryDirectory() as td, lock_file(p(td, 'lock')):
            unlink(p(td, 'lock'))


@pytest.mark.inttest
def test_early_release():
    '''
    Releasing the lock early is allowed although probably not advisable
    '''
    with TemporaryDirectory() as td, lock_file(p(td, 'lock')) as lock:
        lock.release()
