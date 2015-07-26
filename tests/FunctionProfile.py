import re
import os
import json
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

