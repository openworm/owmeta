import unittest
import functools
import cProfile

import FunctionProfile


class ExecutionProfileSuite(unittest.TestSuite):

    def profile(self, f):
        """
        :param f: instancemethod to be wrapped
        :return: Wrapped function that outputs profiling data.
        """
        @functools.wraps(f)
        def wrapper(*args, **kwds):
            # cProfile Prologue
            pr = cProfile.Profile()
            pr.enable()

            result = f(*args, **kwds)

            # cProfile Epilogue
            pr.disable()
            function_profile = FunctionProfile.FunctionProfile(pr, f.im_func.func_name)
            print "\n" + \
                  "\nTest: " + str(function_profile.function_name) + \
                  "\nCumulative Time: " + str(function_profile.cumulative_time)

            return result

        return wrapper

    def __init__(self, *args, **kwargs):
        """
        :param decorator: Decorator function to wrap all tests.  Overrides the default profiling code (profile)
        """
        try:
            # If the "decorator" keyword argument is passed, use custom method wrapper.
            self.decorator = kwargs.pop("decorator")
            if not callable(self.decorator):
                raise ValueError("DecoratorSuite kwarg 'decorator' must be callable.")
        except KeyError:
            # Default to the performance regression wrapper
            self.decorator = self.profile

        super(ExecutionProfileSuite, self).__init__(*args, **kwargs)

    def addTest(self, test):
        """
        :param test: Test passed as type unittest.TestSuite or unittest.TestCase
        """
        if isinstance(test, unittest.TestSuite):
            # These appropriate methods are already wrapped, proceed without modifying "test"
            pass
        elif isinstance(test, unittest.TestCase):
            # TestCases represent individual tests.  Running the test case runs the method specified in the string
            # field _testMethodName.  This is the method we wrap.
            original_method = getattr(test, test._testMethodName)
            wrapped_method = self.decorator(original_method)
            setattr(test, test._testMethodName, wrapped_method)
        else:
            # This should not happen.
            raise ValueError("Unexpected Test Type encountered while decorating test: " + str(type(test)))

        # Call parent method
        super(ExecutionProfileSuite, self).addTest(test)



        


