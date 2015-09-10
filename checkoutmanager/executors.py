#!/usr/bin/env python
# -*- coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals
from multiprocessing.pool import Pool
import time

from checkoutmanager import utils
from checkoutmanager import reports


def get_executor(single):
    """Return a suitable executor, based on the given flag"""
    if single:
        return _SingleExecutor()
    else:
        return _MultiExecutor()


class _Executor(object):
    def __init__(self):
        self.errors = []
        self.reports = []
        self.parse_errors = []

    def _collector(self, returned):
        """Collect a result.

        If the result is a CommandError, save it for later, and print it's
        message.  else, just print the result directly.

        """
        result, report = returned
        if isinstance(result, utils.CommandError):
            self.errors.append(result)
            result = result.format_msg()
        if isinstance(report, reports.ReportBase):
            self.reports.append(report)
        elif isinstance(report, reports.ParseError):
            self.parse_errors.append(report)
        if not result:
            # Don't print empty lines
            return
        print(result)

    def execute(self, func, args):
        """Execute the given function"""
        raise NotImplementedError("Sub-classes must implement this")

    def wait_for_results(self):
        """Make sure all results have been collected"""
        pass


class _SingleExecutor(_Executor):
    """Execute functions in the same thread and process (sync)"""
    def execute(self, func, args):
        self._collector(func(*args))


class _MultiExecutor(_Executor):
    """Execute functions async in a process pool"""
    def __init__(self):
        super(_MultiExecutor, self).__init__()
        self._children = 0
        self.pool = Pool()

    def _collector(self, result):
        super(_MultiExecutor, self)._collector(result)
        self._children -= 1

    def execute(self, func, args):
        self._children += 1
        self.pool.apply_async(func, args, callback=self._collector)

    def wait_for_results(self):
        self.pool.close()
        # One would have hoped joining the pool would take care of this, but
        # apparently you need to first make sure that all your launched tasks
        # has returned their results properly, before calling join, or you
        # risk a deadlock.
        while self._children > 0:
            time.sleep(0.001)
        self.pool.join()
