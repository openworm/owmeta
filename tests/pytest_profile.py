# This file specified pytest plugins

import cProfile
import pytest
from tests.FunctionProfile import FunctionProfile
import urllib, urllib2
import json

# Module level, to pass state across tests.  This is not multiprocessing-safe.
function_profile_list = []
enabled = False
submit_url = None
commit = None
branch = None
environment = None

def pytest_addoption(parser):
    # TODO Group these
    parser.addoption('--profile', dest='profile', action='store_true',
                     default=False, help='Profile test execution with cProfile')
    parser.addoption('--code-speed-submit', dest='cs_submit', action='store',
                     default=None, help='Submit results as JSON to Codespeed instance at URL')
    parser.addoption('--branch', dest='branch', action='store',
                     default=None, help='Branch name')
    parser.addoption('--commit', dest='commit', action='store',
                     default=None, help='Commit ID')
    parser.addoption('--environment', dest='environment', action='store',
                     default=None, help='Environment')


def pytest_configure(config):
    global enabled, submit_url, commit, branch, environment
    enabled = config.getoption('profile')
    submit_url = config.getoption('cs_submit')
    commit = config.getoption('commit')
    branch = config.getoption('branch')
    environment = config.getoption('environment')

def pytest_runtest_setup(item):
    global enabled
    item.enabled = enabled
    item.profiler = cProfile.Profile()

@pytest.mark.hookwrapper
def pytest_runtest_call(item):
    global function_profile_list

    item.profiler.enable() if item.enabled else None
    outcome = yield
    # outcome.excinfo may be None or a (cls, val, tb) tuple

    res = None if outcome is None else outcome.get_result()
    item.profiler.disable() if item.enabled else None

    # Item's Excinfo will indicate any exceptions thrown
    test_fail = hasattr(item, 'excinfo') and item._excinfo is not None
    if not test_fail and item.enabled:
        # item.listnames() returns list of form: ['PyOpenWorm', 'tests/CellTest.py', 'CellTest', 'test_blast_space']
        fp = FunctionProfile(cprofile=item.profiler, function_name=item.listnames()[-1])
        function_profile_list.append(fp)

def pytest_unconfigure(config):
    global enabled, submit_url, commit, branch, environment
    enabled = config.getoption('profile')
    if not enabled:
        return

    data = map(lambda x: x.to_codespeed_dict(commit=commit, branch=branch, environment=environment), function_profile_list)

    print ", ".join(map(lambda x: x.function_name, function_profile_list))

    try:
        encoded_data = {'json': json.dumps(data)}
        f = urllib2.urlopen(submit_url + 'result/add/json/', urllib.urlencode(encoded_data))
    except urllib2.HTTPError as e:
        print str(e)
        print e.read()
        return
    response = f.read()
    f.close()
    print "Server (%s) response: %s".format(submit_url + "result/add/json/", response)
    print "{} records sumbitted.".format(len(function_profile_list))

