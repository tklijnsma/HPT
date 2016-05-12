#!/usr/bin/env python
"""
Thomas:
"""

########################################
# Imports
########################################


import os
import math
import pickle
from array import array
from glob import glob
from copy import deepcopy


########################################
# ROOT
########################################

import ROOT

# ======================================
# Creates arbitrary histogram name by increasing the counter
rootc = 100
def Get_Hname():
    global rootc
    Hname = 'H' + str(rootc)
    rootc += 1
    return Hname


########################################
# Main class
########################################
    
class Spectra_container:

    # ======================================
    # Initialization

    def __init__( self, analysis_level = 'SHOWERED', cuts = [] ):
        'Initialization'

        # Possibilities are currently 'SHOWERED' and 'CUTS'
        # These root files are structured differently, so they have to be read out differently
        self.analysis_level = analysis_level

        # Cuts to be applied during drawing
        self.cuts = cuts

        # Total fiducial cross section [fb] (from http://arxiv.org/pdf/1508.07819v2.pdf)
        self.total_XS = 32.2

        # Open up a Spectrum() instances for data, kt1, and kg1
        self.data = Spectrum( self, 'data' )
        self.kt1 = Spectrum( self, 'kt1' )
        self.kg1 = Spectrum( self, 'kg1' )

        self.c1 = ROOT.TCanvas("c1","c1",1000,800)
        self.c1.SetGrid()


    # ======================================
    # Access functions

    def Set_data_spectrum( self, bins, values, err_up, err_down, max_pt = None ):

        # Determine max_pt; if not specified, round up to nearest fifty
        if not max_pt:
            round_to_nearest = 50.0
            last_bin_pt = bins[-1] + 1
            max_pt = int(math.ceil(last_bin_pt/round_to_nearest)) * int(round_to_nearest)

        # These are the general variables used to set the bins of all spectra
        self.n_pt_bins = len(bins)
        self.pt_bins = bins + [ max_pt ]

        # Load into Spectrum() instance
        self.data.Set_pt_bins( self.pt_bins )
        self.data.Set_values_from_list( values, err_up, err_down )

        # Also set pt_bins for the other Spectrum() instances
        self.kt1.Set_pt_bins( self.pt_bins )
        self.kg1.Set_pt_bins( self.pt_bins )




class Spectrum:

    # ======================================
    # Initialization

    def __init__( self, container, name ):
        
        # Pointer to container class
        self.container = container
        
        # Name of the spectrum
        self.name = name


    def Set_pt_bins( self, pt_bins ):
        self.n_pt_bins = len(pt_bins) - 1
        self.pt_bins = pt_bins


    def Set_values_from_list( self, values, err_up = [], err_down = [] ):
        self.values = values
        self.err_up = err_up
        self.err_down = err_down


    def Set_values_from_root_file( self, root_file, Verbose = False ):
        self.root_file = root_file

        if not os.path.isfile( root_file ):
            print 'Error: root_file {0} does not exist'.format(root_file)
            return

        # Unique histogram name
        Hname = Get_Hname()
        
        # Title
        Htitle = self.name

        # Open the tree
        #   Spectra can be made for showered root files (no cuts applied)
        #   or cut root files (through the flashgg framework)

        # Open file pointer
        root_fp = ROOT.TFile( root_file )

        if self.container.analysis_level == 'SHOWERED':

            # Get Events tree
            tree = root_fp.Get('Events')
            tree.SetAlias( "gp", "Events.recoGenParticles_genParticles__GEN.obj" )

            #draw_str = 'gp.pt_>>{0}'.format( Hname )
            #sel_str  = 'gp.status_==22&&gp.pdgId_==25'

            # Create the histogram
            H = ROOT.TH1F( Hname, Htitle, self.n_pt_bins, array( 'd', self.pt_bins ) )

            draw_str = 'gp.pt()>>{0}'.format( Hname )
            sel_str  = 'gp.status()==22&&gp.pdgId()==25'

            if Verbose:
                print 'Applying draw and selection strings for {0}:'.format(self.name)
                print '  tree.Draw("{0}", "{1}")'.format( draw_str, sel_str )
            tree.Draw(draw_str, sel_str)


        elif self.container.analysis_level == 'CUTS':

            # Enter the directory and create the histogram there
            root_fp.cd('genDiphotonDumper/trees')

            # Create histogram in this directory
            H = ROOT.TH1F( Hname, Htitle, self.n_pt_bins, array( 'd', self.pt_bins ) )

            # Define the tree
            tree  = ROOT.gDirectory.Get( 'ggH_all' )

            # Build the selection string
            #   Start with always true (1.0) and appends with "&& condition"
            sel_str = '1.0'
            for cut in self.container.cuts:
                sel_str += '&& (' + cut + ')'

            print '    Built the following selection string:'
            print sel_str

            tree.Draw( 'pt>>' + Hname, sel_str )
            


        if H.GetEntries() == 0.0:
            print '\nError: Retrieved histogram is empty'
            #return

        # Add the overflow bin to the last bin
        overflow = H.GetBinContent( self.n_pt_bins + 1 )
        H.SetBinContent( self.n_pt_bins,
                              H.GetBinContent( self.n_pt_bins ) + overflow )
        if Verbose:
            print 'Adding {0} entries from overflow to the last bin (bin {1})'.format(
                overflow, H.GetNbinsX() )

        # Set unnormalized values by reading bin contents from the histogram
        self.unnormalized_values = \
            [ H.GetBinContent(i+1) for i in range(self.n_pt_bins) ]

        # Normlize w.r.t. total fiducial cross section
        self.normalization = self.container.total_XS / sum(self.unnormalized_values)
        self.values = [ self.normalization * i for i in self.unnormalized_values ]

        # Deepcopy H into self.H to make sure histogram persists
        self.H = deepcopy( H )

        # Read histogram into arrays
        self.Set_values_from_histogram()

        # Save histogram to .pickle to avoid constant redrawing
        with open( 'H_' + self.name + '.pickle', 'wb' ) as pickle_fp:
            pickle.dump( H, pickle_fp )


    def Set_values_from_pickle_file( self, pickle_file, Verbose = False ):

        with open( pickle_file, 'rb' ) as pickle_fp:
            self.H = pickle.load( pickle_fp )

        # Read histogram into arrays
        self.Set_values_from_histogram()


    def Set_values_from_histogram( self ):
        H = self.H

        # Set unnormalized values by reading bin contents from the histogram
        self.unnormalized_values = \
            [ H.GetBinContent(i+1) for i in range(self.n_pt_bins) ]

        # Normlize w.r.t. total fiducial cross section
        self.normalization = self.container.total_XS / sum(self.unnormalized_values)
        self.values = [ self.normalization * i for i in self.unnormalized_values ]


    def Print_H( self, out_filename = None ):

        # Get filename from title if not specified
        if not out_filename:
            out_filename = self.H.GetTitle()

        self.container.c1.Clear()
        self.H.Draw()
        self.container.c1.Print( out_filename + '.pdf', 'pdf' )








########################################
# Functions
########################################


