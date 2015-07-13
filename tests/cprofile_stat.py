import sys
import cProfile
import pstats

if len(sys.argv) != 2:
    print 'Performance data file required. You have ' + str(len(sys.argv) - 1) + ' arguments\n'
    sys.exit()
else:
    stats = pstats.Stats(sys.argv[1])
    # stats.sort_stats('time','calls')
    # stats.print_stats()
    stats.sort_stats('cumulative','time','calls')
    stats.print_stats('PyOpenWorm')

