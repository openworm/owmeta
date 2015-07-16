import numpy as np
import cProfile
import pstats


class FunctionProfile(object):

    def __init__(self, function_tuple, stats_object):
        """
        :param function_tuple: Function tuple (filename, line #, function name), retrieve from Stats' get_print_list(.)
        :param stats_object: Stats object returned from stats.stats[function_tuple]

        # Example usage:
        >>> import numpy as np
        >>> import cProfile
        >>> import pstats
        >>> pr = cProfile.Profile()
        >>> pr.enable()
        >>> np.random.random(50000)
        >>> pr.disable()
        >>>
        >>> stats = pstats.Stats(pr)
        >>> stats.sort_stats('cumulative')
        >>> width, list = stats.get_print_list("")
        >>> for func_tuple in list:
        >>>     function_profile = FunctionProfile(func_tuple, stats.stats[func_tuple])

        """
        # stats.stats[func_tuple] gives us:
        #  (# primitive (non-recursive) calls , # calls, total_time, cumulative_time, dictionary of callers)
        self.primitve_calls = stats_object[0]
        self.calls = stats_object[1]
        self.total_time = stats_object[2]
        self.cumulative_time = stats_object[3]
        self.callers = stats_object[4]

def main():

    pr = cProfile.Profile()
    pr.enable()
    x = np.std(np.random.random(50000))
    x = np.var(np.random.random(100000))
    x = np.diff(np.random.random(1000000))
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    width, list = stats.get_print_list("")

    for func_tuple in list:

        # func_tuple: (filename, line #, function name)
        print func_tuple
        # ('~', 0, "<method 'random_sample' of 'mtrand.RandomState' objects>")

        # stats.stats[func_tuple] gives us:
        #  (# primitive (non-recursive) calls , # calls, total_time, cumulative_time, dictionary of callers)
        print stats.stats[func_tuple]
        # (3, 3, 0.023063999999999998, 0.023063999999999998, {})

        function_profile = FunctionProfile(func_tuple, stats.stats[func_tuple])
        print dir(stats.stats[func_tuple])

        print "\n"

    stats.print_stats()


    # cc, nc, tt, ct, callers
    # 3    0.023    0.008    0.023    0.008 {method 'random_sample' of 'mtrand.RandomState' objects}

if __name__ == "__main__":
    main()