import sys
import cProfile
import pstats

if len(sys.argv) != 2:
    print 'Performance data file required. You have ' + str(len(sys.argv) - 1) + ' arguments\n'
    sys.exit()
else:
    stats = pstats.Stats(sys.argv[1])
# This configuration generates somewhat more appropriate user-function focused data
#   sorted by cumulative time which includes the time of calls further down the callstack.
    stats.sort_stats('cumulative','time','calls')
#    stats.sort_stats('time','calls')

# This configuration filters the output so only user-functions will show up.
    stats.print_stats('owmeta')
#    stats.print_stats()

