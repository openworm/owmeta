import re
import os
import numpy as np
import pstats
import cProfile


def get_method_name(profile_string):
    """
    :param profile_string: String from Stats object, of the form:
        "<method 'random_sample' of 'mtrand.RandomState' objects>"
    :returns: Method name.
    """
    return re.match(r"^<method \'(?P<method_name>[^']+)", profile_string).group("method_name")


class FunctionProfile(object):

    def __init__(self, cprofile, function_name):
        """
        :param function_tuple: Function tuple (filename, line #, function name), retrieve from Stats' get_print_list(.)
        :param stats_object: Stats object

        # Example usage:
        >>> pr = cProfile.Profile()
        >>> pr.enable()
        >>> x = np.var(np.random.random(100000))
        >>> pr.disable()
        >>> function_profile = FunctionProfile(pr, "var")
        >>> print function_profile
        """
        stats = pstats.Stats(cprofile, stream=open(os.devnull, "w"))

        width, lst = stats.get_print_list("")

        try:
            # function_tuple = filter(lambda func_tuple: function_name == func_tuple[2], lst)[0]
            function_tuple = filter(lambda func_tuple: function_name in func_tuple[2], lst)[0]
        except IndexError:
            # Could not find function_name in lst
            possible_methods = ", ".join(x[2] for x in lst)
            raise ValueError("Function Profile received invalid function name.  Options are: " + str(possible_methods))

        # stats.stats[func_tuple] returns tuple of the form:
        #  (# primitive (non-recursive) calls , # calls, total_time, cumulative_time, dictionary of callers)
        stats_tuple = stats.stats[function_tuple]

        self.function_name   = function_name
        self.primitive_calls = stats_tuple[0]
        self.calls = stats_tuple[1]
        self.total_time = stats_tuple[2]
        self.cumulative_time = stats_tuple[3]
        self.callers = stats_tuple[4]

    def __str__(self):
        l = []
        l.append("Function Name: " + self.function_name)
        l.append("Primitive Calls: " + str(self.primitive_calls))
        l.append("Calls: " + str(self.calls))
        l.append("Total Time: " + str(self.total_time))
        l.append("Cumulative Time: " + str(self.cumulative_time))
        # l.append("Callers: " + str(self.callers))
        return "\n".join(l)


def main():
    pr = cProfile.Profile()
    pr.enable()
    x = np.var(np.random.random(100000))
    pr.disable()
    function_profile = FunctionProfile(pr, "var")
    print function_profile


if __name__ == "__main__":
    main()