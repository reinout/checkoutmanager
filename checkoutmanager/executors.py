#!/usr/bin/env python
# -*- coding: utf-8

import time
from multiprocessing.pool import Pool
from checkoutmanager import utils


class Executor(object):
    def __init__(self):
        self.errors = []
        self.children = 0

    def apply(self, func, args):
        self.children += 1

    def collector(self, result):
        self.children -= 1
        if isinstance(result, utils.CommandError):
            self.errors.append(result)
            result = result.format_msg()
        print(result)


class SingleExecutor(Executor):
    def apply(self, func, args):
        super(SingleExecutor, self).apply(func, args)
        self.collector(apply(func, args))

    def finish(self):
        pass


class MultiExecutor(Executor):
    def __init__(self):
        super(MultiExecutor, self).__init__()
        self.pool = Pool()

    def apply(self, func, args):
        super(MultiExecutor, self).apply(func, args)
        self.pool.apply_async(func, args, callback=self.collector)

    def finish(self):
        self.pool.close()
        while self.children > 0:
            time.sleep(0.001)
        self.pool.join()