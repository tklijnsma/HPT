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


    input_root_file = os.environ['SHOWEREDROOTPATH'] + '/{0}/Showered.root'.format( args[0] )

    output_root_file = os.environ['FLASHBASE'] + '/flashgg_{0}.root'.format( os.environ['RUNNAME'] )

    hgg = hgg_template.replace( '###INPUTROOTFILE', input_root_file ).replace( '###OUTPUTROOTFILE', output_root_file )

    print hgg




########################################
# Configuration template
########################################

hgg_template = """#!/usr/bin/env cmsRun

import FWCore.ParameterSet.Config as cms
import FWCore.Utilities.FileUtils as FileUtils

process = cms.Process("Analysis")

#
# general stuff
#
process.load("FWCore.MessageService.MessageLogger_cfi")

process.load("PhysicsTools.PatAlgos.slimming.genParticles_cff")
process.offlineSlimmedPrimaryVertices = cms.EDProducer("DummyVertexProducer")

process.load("flashgg.MicroAOD.flashggGenPhotons_cfi")
process.load("flashgg.MicroAOD.flashggGenPhotonsExtra_cfi")
process.load("flashgg.MicroAOD.flashggGenDiPhotons_cfi")

# T: These seem to be overwritten by the job options
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32( 1000 )


#
# load job options
#
from flashgg.MetaData.JobConfig import customize
#customize.setDefault("maxEvents",10000)
customize.setDefault("maxEvents",-1)
customize.setDefault("targetLumi",1.e+3)
customize.options.setDefault(
    "inputFiles",

    # Which file to run over
    'file:###INPUTROOTFILE',
    )

import FWCore.ParameterSet.VarParsing as VarParsing
customize.options.register ('massCut',
                            100, # default value
                            VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                            VarParsing.VarParsing.varType.float,          # string, int, or float
                            "massCut")
customize.options.register ('ptLead',
                            1./3., # default value
                            VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                            VarParsing.VarParsing.varType.float,          # string, int, or float
                            "ptLead")
customize.options.register ('ptSublead',
                            1./4., # default value
                            VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                            VarParsing.VarParsing.varType.float,          # string, int, or float
                            "ptSublead")

customize.parse()

#
# input and output
#
process.source = cms.Source(
    "PoolSource",
    fileNames=cms.untracked.vstring(
        )
)
process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string("###OUTPUTROOTFILE.root")
)


#
# analysis configuration
#
process.myGenDiPhotons = cms.EDFilter("GenDiPhotonSelector",
    cut = cms.string(
        '1.0'
        '&& mass > %1.2f '                                                ## mass cut
        '&& leadingPhoton.pt > %1.2f*mass'                             ## scaling pt cuts
        '&& subLeadingPhoton.pt > %1.2f*mass'                          ## 
        '&& leadingExtra.type == 1 && subLeadingExtra.type == 1'       ## select prompt photons
        '&& leadingExtra.genIso < 10. && subLeadingExtra.genIso < 10.' ## gen-level isolation
        '&& (abs(leadingPhoton.eta)    < 2.5    && abs(subLeadingPhoton.eta) < 2.5  )' ## eta acceptance
        '&& (abs(leadingPhoton.eta)    < 1.4442 || abs(leadingPhoton.eta)    > 1.566)' ## no EB-EE gap
        '&& (abs(subLeadingPhoton.eta) < 1.4442 || abs(subLeadingPhoton.eta) > 1.566)' ## 
         % (
             customize.options.massCut,
             customize.options.ptLead,
             customize.options.ptSublead
             )
        ),
    src = cms.InputTag("flashggGenDiPhotons")
    )


import flashgg.Taggers.dumperConfigTools as cfgTools
from flashgg.Taggers.genDiphotonDumper_cfi import genDiphotonDumper
process.genDiphotonDumper = genDiphotonDumper.clone(
    src = cms.InputTag('myGenDiPhotons'),
    maxCandPerEvent = cms.int32(1),
    processId = cms.string("ggH"),
    nameTemplate = cms.untracked.string("$PROCESS_$LABEL_$SUBCAT"),
    dumpTrees = cms.untracked.bool(True)
)
cfgTools.addCategories(process.genDiphotonDumper,
                       [("all","1",0),  # category definition: (<name>,<selection>,<num_subcats>)
                        ## ("EB","max(abs(leadingPhoton.eta),abs(subLeadingPhoton.eta))<1.4442",0),
                        ## ("EE","1",0)
                        ],
                       variables=["mass","pt","rapidity",
                                  "leadPt := leadingPhoton.pt",
                                  "subeadPt := subLeadingPhoton.pt",
                                  ## add more variables here
                                  ],
                       histograms=["genMass>>genmass(1500,0,15000)",
                                   ## can directly draw 
                                   ]
                       )



process.options = cms.untracked.PSet(
    allowUnscheduled = cms.untracked.bool(True)
)

process.p = cms.Path(process.genDiphotonDumper)


# 
customize(process)

## print process.dumpPython()"""


########################################
# End of Main
########################################
if __name__ == "__main__":
    main()



