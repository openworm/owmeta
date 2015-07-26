# This file specified pytest plugins

import cProfile
import pytest
from tests.FunctionProfile import FunctionProfile
import sys
import datetime
import pickle
import os
import glob
import collections

# Globals, to pass state across tests.  This is not multiprocessing-safe.
function_profile_list = []
enabled = False

def pytest_addoption(parser):
    parser.addoption('--profile', dest='profile', action='store_true',
                     default=False, help='Profile test execution with cProfile')

def pytest_configure(config):
    global enabled
    enabled = config.getoption('profile')

def pytest_runtest_setup(item):
    global enabled
    item.enabled = enabled
    item.profiler = cProfile.Profile()

def pytest_runtest_call(item):
    item.profiler.enable() if item.enabled else None
    item.runtest()
    item.profiler.disable() if item.enabled else None

def pytest_runtest_teardown(item):
    # Item's Excinfo will indicate any exceptions thrown
    test_fail = hasattr(item, '_excinfo') and item._excinfo is not None
    if not test_fail and item.enabled:
        # item.listnames() returns list of form: ['PyOpenWorm', 'tests/CellTest.py', 'CellTest', 'test_blast_space']
        fp = FunctionProfile(cprofile=item.profiler, function_name=item.listnames()[-1])
        function_profile_list.append(fp)

def pytest_unconfigure(config):
    enabled = config.getoption('profile')
    if not enabled:
        return
    root_dir = os.path.dirname(__file__)
    utc_time_str = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
    # TODO Add git branch to filename
    filename = 'pyopenworm_profile_{}.pkl'.format(utc_time_str)
    file_glob = 'pyopenworm_profile_*.pkl'
    directory_path = os.path.join(root_dir, 'test_data', 'test_profiles')
    relative_path = os.path.join(directory_path, filename)

    try:
        os.mkdir(directory_path) # Create directory if not present
    except OSError:
        pass

    with open(relative_path, 'w') as f:
        pickle.dump(function_profile_list, f)

    if True:
        compare_stats(glob.glob(os.path.join(directory_path, file_glob)))

def compare_stats(files, scale_threshold=1.05):
    """
    :param files: List of files, relative or absolute path
    """
    z = []
    for index, file in enumerate(sorted(files)):
        with open(file, 'r') as f:
            z.append(pickle.load(f))
        if index == len(files) - 1:
            # Last test, record which tests were run this time
            this_run = set(map(lambda x: x.function_name, z[-1]))

    performance_dict = collections.defaultdict(lambda: [])
    for full_run in z:
        for test in full_run:
            performance_dict[test.function_name].append(test)

    for name, lst in performance_dict.iteritems():
        if len(lst) <= 1 or name not in this_run:
            continue
        current = lst[-1]
        previous = lst[-2]
        if current.cumulative_time > previous.cumulative_time * scale_threshold:
            sys.stdout.write('+ <{0}> execution time has increased {1:0.2f}% from {2} ms to {3} ms.'.format(
                name,
                current.cumulative_time / previous.cumulative_time * 100,
                previous.cumulative_time * 1000.0,
                current.cumulative_time * 1000.0,
            ))
        elif current.cumulative_time * scale_threshold < previous.cumulative_time:
            sys.stdout.write('- <{0}> execution time has sped up {1:0.02f}x from {2} ms to {3} ms.'.format(
                name,
                previous.cumulative_time / current.cumulative_time,
                previous.cumulative_time * 1000.0,
                current.cumulative_time * 1000.0,
            ))

