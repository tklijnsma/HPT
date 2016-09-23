#!/usr/bin/env cmsRun

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

process.load("PhysicsTools.PatAlgos.slimming.slimmedGenJets_cfi")
process.load("RecoJets.Configuration.RecoGenJets_cff")

process.load("RecoJets.Configuration.GenJetParticles_cff")
process.load("RecoJets.JetProducers.fixedGridRhoProducer_cfi")

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
    #"/store/user/musella/GluGluSpin0ToGG_W_0p014_M_750_TuneCUEP8M1_8TeV_pythia8/CMSSW_7_4_15-Private-GEN/160119_234019/0000/GluGluSpin0ToGammaGamma_W_0p014_M_750_TuneCUEP8M1_8TeV_pythia8_GEN_1.root",

    #'file:/afs/cern.ch/work/t/tklijnsm/Production/Chain1_RunningGPs/Saved_root_files/kg1_7_6_3/HIG-RunIIWinter15GenOnly-00011.root',
    #'file:/afs/cern.ch/work/t/tklijnsm/Production/Chain1_RunningGPs/Saved_root_files/kt1_7_6_3/HIG-RunIIWinter15GenOnly-00011.root',

    #'file:/afs/cern.ch/work/t/tklijnsm/Production/Chain1_RunningGPs/Saved_root_files/kg1_74_28April/HIG-RunIIWinter15GenOnly-00011.root',
    #'file:/afs/cern.ch/work/t/tklijnsm/Production/Chain1_RunningGPs/Saved_root_files/kt1_74_28April/HIG-RunIIWinter15GenOnly-00011.root',

    'file:###INPUT'

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
        #'/afs/cern.ch/work/t/tklijnsm/Production/Chain1_RunningGPs/Saved_root_files/kg1_7_6_3/HIG-RunIIWinter15GenOnly-00011.root',
        )
)
process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string("test.root")
)


#
# analysis configuration
#
process.myGenDiPhotons = cms.EDFilter("GenDiPhotonSelector",
    cut = cms.string(
        '1.0 > 0.0'
        # '&& abs(mass-125.)<0.2 '                                                ## mass cut'
        # '&& mass > %1.2f '                                                ## mass cut
        # '&& leadingPhoton.pt > %1.2f*mass'                             ## scaling pt cuts
        # '&& subLeadingPhoton.pt > %1.2f*mass'                          ## 
        # #'&& leadingExtra.type == 1 && subLeadingExtra.type == 1'       ## select prompt photons
        # '&& leadingExtra.genIso < 10. && subLeadingExtra.genIso < 10.' ## gen-level isolation
        # '&& (abs(leadingPhoton.eta)    < 2.5    && abs(subLeadingPhoton.eta) < 2.5  )' ## eta acceptance
        # '&& (abs(leadingPhoton.eta)    < 1.4442 || abs(leadingPhoton.eta)    > 1.566)' ## no EB-EE gap
        # '&& (abs(subLeadingPhoton.eta) < 1.4442 || abs(subLeadingPhoton.eta) > 1.566)' ## 
        #  % (
        #      customize.options.massCut,
        #      customize.options.ptLead,
        #      customize.options.ptSublead
        #      )
        ),
    src = cms.InputTag("flashggGenDiPhotons")
    )


# process.filteredGenJetsEta2p5 = cms.EDFilter(
#     "GenJetSelector",
#     src=cms.InputTag("genJetCollection"),
#     cut=cms.string("pt>%f && abs(eta)<2.5" % jetPtCut),
#     )
process.filteredGenJetsEta4p7 = cms.EDFilter(
    "GenJetSelector",
    src=cms.InputTag("slimmedGenJets"),
    cut=cms.string("pt>30 && abs(eta)<4.7"),
    )
# process.flashggGenHadronicActivity2p5 = cms.EDProducer(
#     "FlashggGenHadronicActivityProducer",
#     src=cms.InputTag("filteredGenJetsEta2p5"),
#     veto=cms.InputTag(genDiphotons)
#     )
process.flashggGenHadronicActivity4p7 = cms.EDProducer(
    "FlashggGenHadronicActivityProducer",
    src=cms.InputTag("filteredGenJetsEta4p7"),
    veto=cms.InputTag("myGenDiPhotons")
    )



import flashgg.Taggers.dumperConfigTools as cfgTools
from flashgg.Taggers.genDiphotonDumper_cfi import genDiphotonDumper
process.genDiphotonDumper = genDiphotonDumper.clone(
    src = cms.InputTag('myGenDiPhotons'),
    maxCandPerEvent = cms.int32(1),
    processId = cms.string("ggH"),
    nameTemplate = cms.untracked.string("$PROCESS_$LABEL_$SUBCAT"),
    dumpTrees = cms.untracked.bool(True)
    # outputFileName = cms.untracked.string("ditiseentest.root")
    )

from flashgg.Taggers.globalVariables_cff import globalVariables
process.genDiphotonDumper.dumpGlobalVariables = True
process.genDiphotonDumper.globalVariables = cms.PSet(
    extraFloats=cms.PSet()
    # outputFileName = cms.untracked.string("ditiseentest.root")
    )


cfgTools.addGlobalFloats(
    process,
    # dumper.globalVariables, # dumper was not defined
    process.genDiphotonDumper.globalVariables,
    "flashggGenHadronicActivity4p7",
    [
        "nJets4p7 := numberOfDaughters",
         "jet0Pt :=       ? numberOfDaughters > 0 ? daughter(0).pt : 0",
         "jet0Rapidity := ? numberOfDaughters > 0 ? daughter(0).rapidity : 0",
        ]
    )


cfgTools.addCategories(process.genDiphotonDumper,
    [ ("all","1",0),  # category definition: (<name>,<selection>,<num_subcats>)
                      ## ("EB","max(abs(leadingPhoton.eta),abs(subLeadingPhoton.eta))<1.4442",0),
                      ## ("EE","1",0)
        ],
    variables=[
        "mass",
        "pt",
        "rapidity",

        "leadPt  := leadingPhoton.pt",
        "leadEta := leadingPhoton.eta",
        "leadPhi := leadingPhoton.phi",

        "leadExtraType   := leadingExtra.type",
        "leadExtraGenIso := leadingExtra.genIso",
        
        "subLeadPt  := subLeadingPhoton.pt",
        "subLeadEta := subLeadingPhoton.eta",
        "subLeadPhi := subLeadingPhoton.phi",

        "subLeadExtraType   := subLeadingExtra.type",
        "subLeadExtraGenIso := subLeadingExtra.genIso",

        ],
    histograms=[
        "genMass>>genmass(1500,0,15000)",
        ## can directly draw 
        ]
    )



process.options = cms.untracked.PSet(
    allowUnscheduled = cms.untracked.bool(True)
)

process.p = cms.Path(process.genDiphotonDumper)


# 
customize(process)

## print process.dumpPython()
