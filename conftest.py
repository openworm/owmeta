from __future__ import print_function
from _pytest.runner import runtestprotocol
# This (Python) file is executed before the py.test suite runs.

# This line specifies where to look for plugins, using python dot notation w.r.t. current directory.
pytest_plugins = 'tests.pytest_profile'


def pytest_runtest_protocol(item, nextitem):
    print(str(item.name) + '...', end='')
    reports = runtestprotocol(item, nextitem=nextitem)
    for report in reports:
        if report.when == 'call':
            print(report.outcome)
    return True
