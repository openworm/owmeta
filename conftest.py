# This file specified pytest plugins

import cProfile
import pytest
from tests.FunctionProfile import FunctionProfile
import sys

def println(x):
    sys.stdout.write(str(x) + "\n")

def pytest_runtest_setup(item):
    item.profiler = cProfile.Profile()
   
def pytest_runtest_call(item):
    item.profiler.enable() # Must be last method call in setup()
    item.runtest()
    item.profiler.disable() # Must be first method call in teardown()

def pytest_runtest_makereport(item, call):
    if not call.excinfo:
        # item.listnames() returns list of form: ['PyOpenWorm', 'tests/CellTest.py', 'CellTest', 'test_blast_space']
        function_profile = FunctionProfile(item.profiler, item.listnames()[-1])
        println(function_profile)

