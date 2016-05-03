#!/usr/bin/env python
"""
Thomas
"""

########################################
# Imports
########################################

import sys


########################################
# Main
########################################

def main():

    args = sys.argv[1:]

    if len(args) == 0:
        print 'Need input parameters'
        return
    elif len(args) == 1:
        runname = args[0]
        n_events = 20000
    else:
        runname = args[0]
        n_events = int(args[1])


    fragment_template = """import FWCore.ParameterSet.Config as cms
externalLHEProducer = cms.EDProducer('ExternalLHEProducer',
    args = cms.vstring('{0}'),
    nEvents = cms.untracked.uint32({1}),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
    )"""

    fragment = fragment_template.format( runname, n_events )


    print fragment


########################################
# End of Main
########################################
if __name__ == "__main__":
    main()