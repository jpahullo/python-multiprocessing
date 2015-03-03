"""
    Multiprocessing in python
    Copyright (C) 2015 Jordi Pujol-Ahullo <jordi.pujol@urv.cat>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import py_ecc
import random
import multiprocessing
import logging

def _run_tests():
    """
    This runs all unitary tests from the py_ecc package.

    In particular:
        py_ecc.rs_code._test()
        py_ecc.file_ecc._test()
    """
    print "Running Reed Salomon self tests...",
    print py_ecc.rs_code._test(), ". Done!"
    print "Running self tests for error correction on files...",
    print py_ecc.file_ecc._test(), ". Done!"

def worker(data):
    """
    This worker simply returns the square value.
    """
    return data*data


def test_pool(size):
    """
    This test runs a pool of processes and calculates the squares of a list of
    integer values.
    """
    print "### Running test_pool with {} processes".format(size)
    p = multiprocessing.Pool(size)
    data = range(3)

    print data, "=>", p.map(worker, data)
    p.terminate()
    p.join()
    print ""

def worker2(data):
    """
    This worker calculates the square of the integers from the given list.
    """
    work = []
    for v in data:
        work.append(v*v)
    return work

def test_pool2(size):
    """
    This test runs a pool of processes and calculates the square values
    from a list of list of integers.
    """
    print "### Running test_pool2 with {} processes".format(size)
    p = multiprocessing.Pool(size)
    data = [range(2*i) for i in range(2*size)]

    returnedData = p.map(worker2, data)
    for i in range(len(data)):
        print data[i]
        print returnedData[i]
        print ""

    p.terminate()
    p.join()

def fail_workers(pool, failures):
    """
    This function emulates failing nodes/processes by terminating the
    number of "failures" processes from the "pool".
    """
    if failures > pool._processes:
        raise Exception("You want to fail {} workers from a total of {}, but you can't!!".format(failures, pool._processes))

    ids = random.sample(range(pool._processes), failures)
    for i in ids:
        "emulating a worker fails via its terminate()"
        pool._pool[i].terminate()
        pool._pool[i].join()

    "after failing processes, we need to recover the amount of processes in the pool"
    pool._maintain_pool()

def test_pool_failing_workers(size, failures):
    """
    This test emulates failing "failures" workers from a pool of "size" number of workers.
    """
    print "### Running pool test and emulate workers stop randomly"
    #enable_debug()
    p = multiprocessing.Pool(size)
    print "Workers => ", p._pool
    print "Workers to make fail:", failures
    fail_workers(p, failures)
    print "Workers after failures:", p._pool
    print ""
    p.terminate()
    p.join()

def who_i_am(data):
    """
    The job of this worker is simply tell who it is ;-)
    """
    print "Hi! I'm {} and I'm processing {}!".format(multiprocessing.current_process().name, data)

def test_pool_who_i_am(size):
    """
    This test shows the way of knowing which process is dealing with
    each piece of data.
    We discover that the load is not uniformly distributed among processes, but data-ordered.
    """
    print "### Running pool test for process introspection"
    p = multiprocessing.Pool(size)
    data = range(size*2)
    datalist = [[i, i+1] for i in range(2*size)]
    "this time, we don't expect any result from the workers."
    p.map(who_i_am, data)
    p.map(who_i_am, datalist)
    print ""
    p.terminate()
    p.join()

def test_pool_who_i_am_uniform(size):
    """
    This test forces a uniform distribution of workload among processes.
    To do so, we implement a pool of Pools for simplicity.
    """
    print "### Running pool test for uniform distribution of workload"
    p = [multiprocessing.Pool(1) for i in range(size)]

    data = range(size*2)
    datalist = [[i] for i in range(2*size)]
    datalist2 = [[i, i+1] for i in range(2*size)]
    "this time, we don't expect any result from the workers."
    "p.map(who_i_am, data)"
    for i, datum in enumerate(data):
        p[i%size].apply(who_i_am, (datum,))

    "p.map(who_i_am, datalist)"
    for i, datum in enumerate(datalist):
        p[i%size].apply(who_i_am, (datum,))

    "p.map(who_i_am, datalist2)"
    for i, datum in enumerate(datalist2):
        p[i%size].apply(who_i_am, (datum,))

    for pool in p:
        pool.terminate()
        pool.join()
    print ""


def enable_debug():
    """
    Enables the full debug, including for sub processes.
    """
    logger = multiprocessing.log_to_stderr(logging.DEBUG)
    logger.setLevel(multiprocessing.SUBDEBUG)

if __name__ == "__main__":
    test_pool(5)
    test_pool2(10)
    test_pool_failing_workers(5,2)
    test_pool_who_i_am(5)
    test_pool_who_i_am_uniform(5)

