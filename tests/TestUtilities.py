import os

skippedTest = '@unittest.skip'
expectedFailure = '@unittest.expectedFailure'

# The boolean count is to make sure that multiple new lines aren't printed
# in the event that multiple files have neither skipped tests nor
# expected failures.

for fname in os.listdir('.'):
    if os.path.isfile(fname) and fname[-3:] == ".py" and fname != 'TestUtilities.py':
        with open(fname) as f:
            count = False
            for line in f:
                if skippedTest in line:
                    print 'found skipped test in file %s' %fname
                    count = True
                elif expectedFailure in line:
                    print 'found expected failure in file %s' %fname
                    count = True
            if count:
                print '\n'
                count = False
