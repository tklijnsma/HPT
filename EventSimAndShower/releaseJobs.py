import sys
sys.path.append('src')

import argparse
import os

from array import array
from copy import deepcopy


########################################
# Main
########################################

pwd = os.getcwd()
jobscriptDir = os.path.join(pwd, 'jobscripts' )
stdDir       = os.path.join(pwd, 'std' )
for directory in [ jobscriptDir, stdDir ]:
    if not os.path.isdir(directory): os.makedirs(directory)


def main():

    parser = argparse.ArgumentParser()
    # parser.add_argument( 'tarballs', metavar='N', type=str, nargs='*', help='Give a list of tarballs for which to submit jobs' )
    # parser.add_argument( '-n', '--nevents', type=int, default=100000, help='number of events' )
    parser.add_argument( '--test', action='store_true', help='Does not submit the job, but creates the .sh file and prints')
    args = parser.parse_args()


    tarballs = [
        '/mnt/t3nfs01/data01/shome/tklijnsm/HPT/Make_gridpacks/Saved_tarballs/kg1_gg_H.tgz',
        '/mnt/t3nfs01/data01/shome/tklijnsm/HPT/Make_gridpacks/Saved_tarballs/kt1_gg_H_quark-mass-effects.tgz'
        ]
    
    nEventsPerJob = 100000
    nJobs = 20

    # Make the jobscripts
    for tarball in tarballs:
        for jobNumber in xrange(nJobs):
            makeJobscript( tarball, nEventsPerJob, jobNumber )

            cmd = 'qsub ' + getTarballJobName( tarball, jobNumber )

            if args.test:
                print 'TEST MODE: would now execute "{0}"'.format(cmd)
            else:
                os.system( cmd )




def makeJobscript( tarball, nEvents, jobNumber ):

    fp = open( getTarballJobName( tarball, jobNumber ), 'w' )
    p = lambda text: fp.write( text + '\n' )


    p( '#$ -q all.q' )

    p( '#$ -o ' + stdDir )
    p( '#$ -e ' + stdDir )

    p( 'cd ' + pwd )

    p( '. runJob.sh {0} {1} {2}'.format(
        tarball, nEvents, jobNumber
        ) )

    fp.close()

    os.system( 'chmod 777 ' + getTarballJobName( tarball, jobNumber )  )


def getTarballJobName( tarball, jobNumber ):
    return '{0}/{1}_job{2}.sh'.format( jobscriptDir, os.path.basename(tarball).rsplit('.',1)[0], jobNumber )




########################################
# End of Main
########################################
if __name__ == "__main__":
    main()