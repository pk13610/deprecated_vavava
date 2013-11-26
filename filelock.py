#####################################################################
# COPY FROM http://www.gnome.org/~jdub/bzr/planet/2.0/planet/htmltmpl.py
# and inspired from http://www.python.org/pypi/zc.lockfile
# LICENSE: BSD
# Modified by: Limodou(limodou@gmail.com)
# Modified by: vavava, add timeout lock --> try_lock
#####################################################################

__all__ = ['LOCK_EX', 'LOCK_SH', 'LOCK_UN', 'lock_file', 'unlock_file',
           'LockFile', 'LockError']

import os

class LockError(Exception):
    """Couldn't get a lock
    """

LOCKTYPE_FCNTL = 1
LOCKTYPE_MSVCRT = 2
LOCKTYPE = None

try:
    import fcntl
except:
    try:
        import msvcrt
    except:
        LOCKTYPE = None
    else:
        LOCKTYPE = LOCKTYPE_MSVCRT
else:
    LOCKTYPE = LOCKTYPE_FCNTL
LOCK_EX = 1
LOCK_SH = 2
LOCK_UN = 3

def lock_file(f, lock=LOCK_SH):
    try:
        fd = f.fileno()
        if LOCKTYPE == LOCKTYPE_FCNTL:
            if lock == LOCK_SH:
                fcntl.flock(fd, fcntl.LOCK_SH)
            elif lock == LOCK_EX:
                fcntl.flock(fd, fcntl.LOCK_EX)
            elif lock == LOCK_UN:
                fcntl.flock(fd, fcntl.LOCK_UN)
            else:
                raise LockError, "BUG: bad lock in lock_file"
        elif LOCKTYPE == LOCKTYPE_MSVCRT:
            if lock == LOCK_SH:
                # msvcrt does not support shared locks :-(
                msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
            elif lock == LOCK_EX:
                msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
            elif lock == LOCK_UN:
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                raise LockError, "BUG: bad lock in lock_file"
        else:
            raise LockError, "BUG: bad locktype in lock_file"
        return True
    except IOError:
        #raise LockError("Couldn't lock %r" % f.name)
        return False

def unlock_file(f):
    lock_file(f, LOCK_UN)

from vavava.basethread import BaseThread
class LockFile(BaseThread):
    def __init__(self, lockfilename):
        BaseThread.__init__(self)
        self._f = lockfilename
        self._create_flag = False
        self._checkfile()
        self._lock_flag = LOCK_EX
        self._locked = False

    def _checkfile(self):
        if os.path.exists(self._f):
            self._fd = open(self._f, 'rb')
        else:
            dir = os.path.dirname(self._f)
            if dir and not os.path.exists(dir):
                os.makedirs(dir)
            self._fd = open(self._f, 'wb')
            self._create_flag = True

    def lock(self, lock_flag=LOCK_SH):
        if self._locked:
            raise Exception("already locked")
        self._locked = lock_file(self._fd, lock_flag)
        return self._locked

    def try_lock(self,lock_flag=LOCK_EX,timeout=3):
        if self._locked:
            raise Exception("already locked")
        self._lock_flag = lock_flag
        self.running_start()
        self.running_stop()
        self.join(timeout=timeout)
        return self._locked

    def run(self):
        self._locked = lock_file(self._fd, self._lock_flag)

    def close(self):
        unlock_file(self._fd)
        self._fd.close()

    def delete(self):
        self._fd.close()
        os.unlink(self._f)

    def __del__(self):
        if self._locked:
            self.close()
            self.delete()
            print "deleted"
"""
    def try_lock(self,lock_flag=LOCK_SH,tout=3):
        import signal, errno
        from contextlib import contextmanager

        @contextmanager
        def timeout(seconds):
            def timeout_handler(signum, frame):
                pass
            original_handler = signal.signal(signal.SIGALRM, timeout_handler)
            try:
                signal.alarm(seconds)
                yield
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, original_handler)

        with timeout(tout):
            self.lock(lock_flag)
"""

def test():
    import os,time
    cpid = os.fork()
    while True:

        if cpid == 0:
            fl = LockFile(name="file_lock_test.lock")
            fl.lock()
            print "child Locked:",str(fl._locked)
            time.sleep(1)
            fl._unlock()
            print "child locked:",str(fl._locked)
        else:
            ff = LockFile(name="file_lock_test.lock")
            print "parent Locked:",str(ff._locked)
            time.sleep(0.3)
            ff._unlock()
            print "parent Locked:",str(ff._locked)

def test1():
    import time
    fl = LockFile("file_lock_test.lock")
    fl.try_lock(LOCK_EX)
    if not fl._locked:
        print "is locked"
        return
    while True:
        time.sleep(1)
        print "I have lock"

if __name__ == "__main__":
    test1()










