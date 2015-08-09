# This file specified pytest plugins

import pstats
import cProfile
import json
import timeit
import os
import urllib, urllib2
import pytest


# Module level, to pass state across tests.  This is not multiprocessing-safe.
function_profile_list = []
enabled = False
submit_url = None
commit = None
branch = None
environment = None


def pytest_addoption(parser):
    profile_group = parser.getgroup('Performance Profiling', description='Use cProfile to profile execution times of test_* functions.')
    profile_group.addoption('--code-speed-submit', dest='cs_url', action='store',
                     default=None, help='Submit results as JSON to Codespeed instance at URL. ' + \
                     "Must be accompanied by --branch, --commit, and --environment arguments.")
    profile_group.addoption('--branch', dest='branch', action='store',
                     default=None, help='Specify Codespeed "Branch" setting.')
    profile_group.addoption('--commit', dest='commit', action='store',
                     default=None, help='Specify Codespeed "Commit ID" setting.')
    profile_group.addoption('--environment', dest='env', action='store',
                     default=None, help='Specify Codespeed "Environment" setting.')


def pytest_configure(config):
    """
    Called before tests are collected.
    """
    global enabled, submit_url, commit, branch, environment

    # enabled = config.getoption('profile') or config.getoption('cs_submit_url') is not None
    enabled = config.getoption('cs_url') is not None
    submit_url = config.getoption('cs_url')
    commit = config.getoption('commit')
    branch = config.getoption('branch')
    environment = config.getoption('env')

    missing_argument = not commit or not branch or not environment
    if submit_url and missing_argument:
        raise ValueError("If calling with --code-speed-submit, user must supply " +\
                         "--commit, --branch, and --environment arguments.")


@pytest.mark.hookwrapper
def pytest_runtest_call(item):
    """
    Calls once per test.
    """
    global function_profile_list, enabled

    item.enabled = enabled
    item.profiler = cProfile.Profile()

    item.profiler.enable() if item.enabled else None
    outcome = yield
    item.profiler.disable() if item.enabled else None

    result = None if outcome is None else outcome.get_result()

    # Item's excinfo will indicate any exceptions thrown
    if item.enabled and item._excinfo is None:
        # item.listnames() returns list of form: ['PyOpenWorm', 'tests/CellTest.py', 'CellTest', 'test_blast_space']
        fp = FunctionProfile(cprofile=item.profiler, function_name=item.listnames()[-1])
        function_profile_list.append(fp)


def pytest_unconfigure(config):
    """
    Called after all tests are completed.
    """
    global enabled, submit_url, commit, branch, environment

    if not enabled:
        return

    data_int = map(lambda x: x.to_codespeed_dict(commit=commit,
                                                 branch=branch,
                                                 environment=environment,
                                                 benchmark="int"),
                   function_profile_list)
    data_flt = map(lambda x: x.to_codespeed_dict(commit=commit,
                                                 branch=branch,
                                                 environment=environment,
                                                 benchmark="float"),
                   function_profile_list)

    int_time = timeit.timeit('100 * 99', number=500)
    float_time = timeit.timeit('100.5 * 99.2', number=500)

    for elt in data_int:
        # Result should be factor of int operation time
        elt["result_value"] = elt["result_value"] / int_time
    for elt in data_flt:
        # Result should be factor of int operation time
        elt["result_value"] = elt["result_value"] / float_time

    data = data_int + data_flt

    try:
        f = urllib2.urlopen(submit_url + 'result/add/json/',
                            urllib.urlencode({'json': json.dumps(data)}))
        response = f.read()
    except urllib2.HTTPError as e:
        print 'Error while connecting to Codespeed:'
        print 'Exception: {}'.format(str(e))
        print 'HTTP Response: {}'.format(e.read())
        raise e

    if not response.startswith('All result data saved successfully'):
        print "Unexpected response while connecting to Codespeed:"
        raise ValueError('Unexpected response from Codespeed server: {}'.format(response))
    else:
        print "{} test benchmarks sumbitted.".format(len(function_profile_list))


class FunctionProfile(object):

    def __init__(self, *args, **kwargs):
        """
        :param cprofile: Cprofile object created by cProfile.Profile().  Must be paired with function_name parameter.
        :param function_name: Name of function profiled.  Must be paired with cprofile parameter.
        :param json: Create a function profile from a JSON string.  Overridden by cprofile/functionname parameters.

        >>> pr = cProfile.Profile()
        >>> pr.enable()
        >>> x = map(lambda x: x**2, xrange(1000))
        >>> pr.disable()
        >>> function_profile = FunctionProfile(pr, "map")
        >>> print function_profile
        """

        cprofile = kwargs.pop("cprofile", None)
        function_name = kwargs.pop("function_name", None)
        json_str = kwargs.pop("json", None)

        assert (cprofile is not None and function_name is not None) ^ (json_str is not None), \
            "Invalid initialization arguments to FunctionProfile."

        if cprofile is not None and function_name is not None:
            stats = pstats.Stats(cprofile, stream=open(os.devnull, "w"))

            width, lst = stats.get_print_list("")

            try:
                # function_tuple = filter(lambda func_tuple: function_name == func_tuple[2], lst)[0]
                function_tuple = filter(lambda func_tuple: function_name in func_tuple[2], lst)[0]
            except IndexError:
                # Could not find function_name in lst
                possible_methods = ", ".join(x[2] for x in lst)
                raise ValueError("Function Profile received invalid function name " + \
                                 "<{}>.  Options are: {}".format(function_name, str(possible_methods)))

            # stats.stats[func_tuple] returns tuple of the form:
            #  (# primitive (non-recursive) calls , # calls, total_time, cumulative_time, dictionary of callers)
            stats_tuple = stats.stats[function_tuple]
            self.function_name = function_name
            self.primitive_calls = stats_tuple[0]
            self.calls = stats_tuple[1]
            self.total_time = stats_tuple[2]
            self.cumulative_time = stats_tuple[3]
            self.callers = stats_tuple[4]
        elif json_str is not None:
            self._from_json(json_str)
        else:
            raise AssertionError("Invalid initialization arguments to FunctionProfile.")

    def __str__(self):
        l = []
        l.append("Function Name: " + self.function_name)
        l.append("Primitive Calls: " + str(self.primitive_calls))
        l.append("Calls: " + str(self.calls))
        l.append("Total Time: " + str(self.total_time))
        l.append("Cumulative Time: " + str(self.cumulative_time))
        # l.append("Callers: " + str(self.callers))
        return "\n".join(l)

    def _to_json(self):
        return json.dumps(self, default=(lambda o: o.__dict__), sort_keys=True, indent=4)

    def _from_json(self, json_str):
        """
        :param json_str: JSON String (result of previous _to_json)
        :returns: Stats_tuple (same form as stats.stats()[function_tuple])
        :raises: AssertionError if JSON malformed.
        """
        try:
            json_dict = json.loads(json_str)
        except ValueError as e:
            raise AssertionError("Invalid JSON encountered while initializing FunctionProfile: {}".format(json_str) + str(e))

        keys = json_dict.keys()

        error_str = "FunctionProfile received Malformed JSON."

        assert "callers" in keys, error_str
        assert "calls" in keys, error_str
        assert "cumulative_time" in keys, error_str
        assert "function_name" in keys, error_str
        assert "primitive_calls" in keys, error_str
        assert "total_time" in keys, error_str

        assert type(json_dict["callers"]) == dict, error_str
        assert type(json_dict["calls"]) == int, error_str
        assert type(json_dict["cumulative_time"]) == float, error_str
        assert type(json_dict["function_name"]) == unicode, error_str
        assert type(json_dict["primitive_calls"]) == int, error_str
        assert type(json_dict["total_time"]) == float, error_str

        self.callers = json_dict["callers"]
        self.calls = json_dict["calls"]
        self.cumulative_time = json_dict["cumulative_time"]
        self.function_name = json_dict["function_name"]
        self.primitive_calls = json_dict["primitive_calls"]
        self.total_time = json_dict["total_time"]

    def to_codespeed_dict(self, commit="0", branch="dev", environment="Dual Core", benchmark="int"):
        """
        :param commit: Codespeed current commit argument.
        :param branch: Codespeed current branch argument.
        :param environment: Codespeed environment argument.
        :param benchmark: "int" or "float"
        :return: Codespeed formatted dictionary.
        """
        # Currently, Codespeed breaks if a branch named anything other than 'default' is submitted.
        return {
            "commitid": commit,
            "project": "PyOpenWorm",
            "branch": "default",
            "executable": self.function_name,
            "benchmark": benchmark,
            "environment": environment,
            "result_value": self.cumulative_time / self.calls
        }
