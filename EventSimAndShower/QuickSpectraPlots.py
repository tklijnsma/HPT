import sys
sys.path.append('src')


import ROOT
import argparse
import os

from array import array
from copy import deepcopy


########################################
# Main
########################################

ROOT.gROOT.SetBatch(True)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kError;")

print 'Importing root libraries'
ROOT.gSystem.Load("libDataFormatsFWLite.so")
ROOT.AutoLibraryLoader.enable()


c = ROOT.TCanvas( 'c1', 'c1', 800, 600 )
plotdir = 'QuickPlots'
rootc = 1


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument( '--redraw', action='store_true', help='Forces the program to redraw the histograms from the root files')
    parser.add_argument( 'rootfiles', metavar='N', type=str, nargs='+', help='List of root files for which to draw a spectrum')
    parser.add_argument( '--var', type=str, help='specific variable to draw')
    args = parser.parse_args()


    for root_file in args.rootfiles:
        getHistogram( root_file )




def getHistogram( root_file, varname='pt', bins=None ):
    global rootc

    root_fp = ROOT.TFile( root_file )

    # Get Events tree
    tree = root_fp.Get('Events')
    tree.SetAlias( "gp", "Events.recoGenParticles_genParticles__GEN.obj" )

    # Create the histogram
    Hname = 'H' + str(rootc)
    rootc += 1
    
    if not bins:
        H = ROOT.TH1F( Hname, Hname, 100, 0., 300. )
    else:
        H = ROOT.TH1F( Hname, Hname, len(bins)-1, array( 'd', bins ) )

    draw_str = 'gp.{0}()>>{1}'.format( varname, Hname )
    sel_str  = 'gp.status()==22&&gp.pdgId()==25'

    print '  tree.Draw("{0}", "{1}")'.format( draw_str, sel_str )
    tree.Draw(draw_str, sel_str)


    H.Draw()
    SaveCanvas( c, Hname + '.pdf' )






def parseSelString( listOfSelectionStrings ):

    # Copy list so it won't change
    sels = listOfSelectionStrings[:]

    # Start with first one
    sel_str = sels.pop(0)

    # Parse the other parts
    for sel in sels:
        sel_str += '&& (' + sel + ')'

    return sel_str



def SaveCanvas( canvas, outname, plotDirectory=plotdir ):
    if not os.path.isdir( plotDirectory ): os.makedirs(plotDirectory)
    canvas.SaveAs( os.path.join( plotDirectory, outname ) )


########################################
# End of Main
########################################
if __name__ == "__main__":
    main()