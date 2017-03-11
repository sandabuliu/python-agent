import os
from logging import Handler
from logging.handlers import TimedRotatingFileHandler

import time

from portalocker import lock, unlock, LOCK_EX, LOCK_NB, LockException

FORCE_ABSOLUTE_PATH = False


class ConcurrentTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0,
                 encoding=None, delay=0, utc=0, debug=False, supress_abs_warn=False):
        # if the given filename contains no path, we make an absolute path
        if not os.path.isabs(filename):
            if FORCE_ABSOLUTE_PATH or \
                    not os.path.split(filename)[0]:
                filename = os.path.abspath(filename)
            elif not supress_abs_warn:
                from warnings import warn

                warn("The given 'filename' should be an absolute path.  If your "
                     "application calls os.chdir(), your logs may get messed up. "
                     "Use 'supress_abs_warn=True' to hide this message.")
        TimedRotatingFileHandler.__init__(self, filename, when, interval, backupCount, encoding, delay, utc)
        self.currentSuffix = time.strftime(self.suffix, time.localtime())
        self.stream_lock = open(filename.replace(".log", "") + ".lock", "w")

    def acquire(self):
        """ Acquire thread and file locks. Also re-opening log file when running
        in 'degraded' mode. """
        # handle thread lock
        Handler.acquire(self)
        lock(self.stream_lock, LOCK_EX)
        if self.stream.closed:
            self.mode = 'a'
            self.stream = self._open()

    def release(self):
        try:
            self.stream.flush()
        except:
            pass
        finally:
            try:
                unlock(self.stream_lock)
            finally:
                # release thread lock
                Handler.release(self)

    def shouldRollover(self, record):
        newSuffix = time.strftime(self.suffix, time.localtime())
        if newSuffix != self.currentSuffix:
            return 1
        return 0

    def doRollover(self):
        if self.stream:
            self.stream.close()
        # get the time that this sequence started at and make it a TimeTuple
        dfn = self.baseFilename + "." + self.currentSuffix
        # dst file exists infers that the other process has renamed the file
        # so just open the basefile again
        if not os.path.exists(dfn):
            os.rename(self.baseFilename, dfn)
        self.mode = 'a'
        self.stream = self._open()
        self.currentSuffix = time.strftime(self.suffix, time.localtime())