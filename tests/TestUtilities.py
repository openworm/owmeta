import os

def findSkippedTests():
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

# Function to list function names in test suite so we can quickly see \
# which ones do not adhere to the proper naming convention.
def listFunctionNames():
        for fname in os.listdir('.'):
            if os.path.isfile(fname) and fname[-3:] == ".py" and fname != 'TestUtilities.py':
                with open(fname) as f:
                    count = False
                    for line in f:
                        check = line.strip()[4:8]
                        if 'def ' in line and check != 'test' and check != '__in':
                            print line.strip() + ' in file ' + fname
                            count = True

                    if count:
                        print '\n'
                        count = False

# Add function to find dummy tests, i.e. ones that are simply marked pass.
# TODO: improve this to list function names
def findDummyTests():
        for fname in os.listdir('.'):
            if os.path.isfile(fname) and fname[-3:] == ".py" and fname != 'TestUtilities.py':
                with open(fname) as f:
                    count = False
                    for line in f:
                        if 'pass' in line:
                            print 'dummy test' + ' in file ' + fname
                            count = True

                    if count:
                        print '\n'
                        count = False
