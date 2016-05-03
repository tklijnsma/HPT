#!/usr/bin/env python
"""
Thomas
"""

########################################
# Imports
########################################

import os
import shutil
import sys
from glob import glob

from time import sleep


########################################
# Main
########################################

def main():

    runnames = sys.argv[1:]

    if len(runnames) == 0:
        print 'Error: No runnames specified'
        return 1

    if not os.path.basename( os.getcwd() ) == 'Make_gridpacks':
        print 'Error: Current directory is {0} instead of Make_gridpacks'.format( os.getcwd() )
        return 1

    makedir = os.getcwd()

    if not os.path.isdir( 'Saved_tarballs' ): os.makedirs( 'Saved_tarballs' )
    if not os.path.isdir( 'output_logs' ): os.makedirs( 'output_logs' )

    checkers = []
    for runname in runnames:
        # Instantiate StatusChecker class
        checker = StatusChecker( runname )
        checkers.append( checker )


    # Start a checking loop
    n_checks = 200
    time_between_checks = 5


    print '\n' + '-'*70
    print 'Starting status checker; n_checks = {0}, time_between_checks = {1}'.format(
        n_checks, time_between_checks )

    for i_check in range(n_checks):

        status = 1
        for checker in checkers:
            status *= checker.Check_status( i_check, n_checks )

        # If all returns were 1, the program can finish
        if status:
            print 'All runs are finished'
            return 0

        # Otherwise sleep
        sleep( time_between_checks )

    print 'Program ended because maximum number of checks was reached'


########################################
# Checker class
########################################

class StatusChecker:
    
    # ======================================
    def __init__( self, runname ):
        self.runname = runname
        self.pwgdir = '{0}/src/genproductions/bin/Powheg/'.format( os.environ['CMSSW_VERSION'] )

        self.Determine_model_and_card()

        self.tgz_file = self.pwgdir + '{0}_{1}.tgz'.format( self.runname, self.model )
        self.log_file = self.pwgdir + 'run_full_{0}.log'.format(self.runname)

        self.run_is_finished = False


    def Determine_model_and_card( self ):

        # Read the model from the MODEL.txt file
        try:
            with open( 'input/{0}/MODEL.txt'.format(self.runname), 'r' ) as MODEL_fp:
                self.model = MODEL_fp.read().strip()
        except IOError:
            print 'There is no MODEL.txt file in input/{0}/'.format(self.runname)
            return 1

        # Look for the .input filename
        try:
            self.inputcard = os.path.basename( glob( 'input/{0}/*.input'.format(self.runname) )[0] )
        except IndexError:
            print 'There are no input cards found in input/{0}/'.format(self.runname)
            return 1


    def Check_status( self, i_check, n_checks ):

        if self.run_is_finished:
            # This run has been sufficiently checked if this var is True
            return 1

        # Look for hints in the log file that there are no errors
        try:
            with open( self.log_file ) as log_fp:
                full_log = log_fp.read()

            self.log_file_exists = True

            if ( True
                and ( 'End of job' in full_log )
                and ( 'Done.' in full_log )
                ):
                self.job_finished = True
            else:
                self.job_finished = False
        
        except IOError:
            self.job_finished = False
            self.log_file_exists = False


        if not self.job_finished:
            print 'Check {0:4}/{1}; Run {2} not yet finished'.format(
                i_check, n_checks, self.runname )

            if not self.log_file_exists:
                print '    .log file for {0} does not exist (yet)!'.format( self.runname )
            # Continue checking
            return 0

        else:

            # Look if the tarball already exists
            self.tgz_exists = os.path.isfile( self.tgz_file )

            # Give a bit more time
            if not self.tgz_exists:
                print 'Tarball {0} does not exist yet, but packing may be slow; waiting for 90 seconds...'.format(
                    self.tgz_file )
                sleep(90)

            # Look again if the tarball exists
            self.tgz_exists = os.path.isfile( self.tgz_file )

            if self.tgz_exists:
                # Everything exited normally
                shutil.copyfile( self.tgz_file, 'Saved_tarballs/' + os.path.basename( self.tgz_file )  )
                shutil.copyfile( self.log_file, 'output_logs/' +    os.path.basename( self.log_file )  )
                print 'Gridpack {0} creation exited normally'.format( self.runname )

            elif not self.tgz_exists:
                # There was probably an error in the creation
                shutil.copyfile( self.log_file, 'output_logs/' + os.path.basename( self.log_file )  )
                print 'Gridpack {0} creation exited abnormally! See the log file for details'.format( self.runname )

            self.run_is_finished = True
            return 1




########################################
# End of Main
########################################
if __name__ == "__main__":
    main()