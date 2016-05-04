#!/usr/bin/env python
"""
Thomas
"""

########################################
# Imports
########################################

import os
import sys


########################################
# Main
########################################

def main():

    args = sys.argv[1:]

    if len(args) == 0:
        print 'Need at least 1 input argument'
        return 0


    # Configuration template
    with open( '{0}/Scripts/cfg_template.py'.format( os.environ['FLASHBASE'] ) ) as template_fp:
        hgg_template = template_fp.read()


    input_root_file = os.environ['SHOWEREDROOTPATH'] + '/{0}/Showered.root'.format( args[0] )
    hgg = hgg_template.replace( '###INPUT', input_root_file )

    print hgg

    #output_root_file = os.environ['FLASHBASE'] + '/flashgg_{0}.root'.format( os.environ['RUNNAME'] )


########################################
# End of Main
########################################
if __name__ == "__main__":
    main()



