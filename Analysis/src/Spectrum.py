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
        # self.total_XS = 32.2

        # Total ggH XS
        self.total_XS = 19.27 * 1000

        # H --> gg BR
        self.Hgg_BR = 2.277E-03

        # Fid XS
        self.fid_XS = lambda acceptance: self.total_XS * self.Hgg_BR * acceptance

        # The 8 TeV analysis integrated luminosity
        self.default_luminosity = 19.7

        # Open up a Spectrum() instances for data, kt1, and kg1
        self.data = Spectrum( self, 'data' )
        self.kt1 = Spectrum( self, 'kt1' )
        self.kg1 = Spectrum( self, 'kg1' )

        self.c1 = ROOT.TCanvas("c1","c1",1000,800)
        self.c1.SetGrid()

        # Checks if the lists for other channels are filled
        self.OC_filled = False

        self.plotdir = 'plots'
        if not os.path.isdir(self.plotdir): os.makedirs(self.plotdir)


        self.vartitle = 'p_{t}'
        self.varunit  = ' [GeV]'


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
        self.data.raw_sum = sum(values)

        # Also set pt_bins for the other Spectrum() instances
        self.kt1.Set_pt_bins( self.pt_bins )
        self.kg1.Set_pt_bins( self.pt_bins )



    def Get_other_channel_contributions( self, OC_rootfile = 'xSec_pToMscaled.root' ):
        OC_rootfp   = ROOT.TFile.Open( OC_rootfile )

        # Other channel contributions
        histnames = [ 'HExp_tth', 'HExp_vbf', 'HExp_zh', 'HExp_wh' ]

        # Result list: Other Channel XS
        self.OC_XS = [ 0. for i in xrange(self.n_pt_bins) ]


        for histname in histnames:
            hist = OC_rootfp.Get(histname)

            for i in xrange(self.n_pt_bins):
                self.OC_XS[i] += hist.GetBinContent(i+1)

        self.OC_filled = True
        OC_rootfp.Close()




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

        self.bin_widths = []
        self.bin_centers = []

        for i in xrange(self.n_pt_bins):
            self.bin_widths.append( self.pt_bins[i+1] - self.pt_bins[i] )
            self.bin_centers.append( 0.5*( self.pt_bins[i+1] + self.pt_bins[i] ) )

        self.half_bin_widths = [ 0.5 * i for i in self.bin_widths ]


        # !!: The last bin width is arbitrary! Just set it to one for now
        #   (centers and half bin widths are only used for plotting, so they don't have to be changed)
        self.bin_widths[-1] = 1.0


    def Set_values_from_list( self, values, err_up = [], err_down = [] ):

        self.values = [ val / bin_width for val, bin_width in zip( values, self.bin_widths ) ]

        self.err_up   = [ err / bin_width for err, bin_width in zip( err_up, self.bin_widths ) ]
        self.err_down = [ err / bin_width for err, bin_width in zip( err_down, self.bin_widths ) ]


    def Set_values_from_root_file( self, root_file, varname = 'pt', Verbose = False ):
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

            draw_str = 'gp.{0}()>>{1}'.format( varname, Hname )
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


            # Drawing without cuts - Needed to calculate acceptance
            tree.Draw( varname + '>> ' + Hname, '' )
            self.Nev_before_cuts = H.GetEntries()


            # Build the selection string
            #   Start with always true (1.0) and appends with "&& condition"
            sel_str = '1.0'
            for cut in self.container.cuts:
                sel_str += '&& (' + cut + ')'

            print '    Built the following selection string:'
            print sel_str

            tree.Draw( varname + '>>' + Hname, sel_str )

            # Calculate acceptance
            self.Nev_after_cuts = H.GetEntries()
            self.acceptance = float(self.Nev_after_cuts) / float(self.Nev_before_cuts)



        if H.GetEntries() == 0.0:
            print '\nError: Retrieved histogram is empty'
            #return

        # Add the overflow bin to the last bin
        overflow = H.GetBinContent( self.n_pt_bins + 1 )
        H.SetBinContent( self.n_pt_bins, H.GetBinContent( self.n_pt_bins ) + overflow )
        H.Sumw2()
        if Verbose:
            print 'Adding {0} entries from overflow to the last bin (bin {1})'.format( overflow, H.GetNbinsX() )

        # Save current histogram to .pickle -- This is pure event count, not divided by bin width
        with open( 'H_' + self.name + '_pureEventCount.pickle', 'wb' ) as pickle_fp:
            pickle.dump( H, pickle_fp )


        # Divide by the bin width (need events per GeV!)
        # --> Skip last bin though, it's arbitrary!
        for i in range( self.n_pt_bins-1 ):
            H.SetBinContent( i+1, H.GetBinContent(i+1) / H.GetXaxis().GetBinWidth(i+1) )
            H.SetBinError(   i+1, H.GetBinError(i+1) / H.GetXaxis().GetBinWidth(i+1) )


        # Set unnormalized values by reading bin contents from the histogram
        self.unnormalized_values = [ H.GetBinContent(i+1) for i in range(self.n_pt_bins) ]


        # Actual normalization factor
        self.normalization = self.container.fid_XS( self.acceptance ) / H.Integral('width')


        if Verbose:
            print '='*50
            print 'Normalizing to fid XS:'
            print '  Total ggH XS: ' + str( self.container.total_XS )
            print '  H -> gg BR:   ' + str( self.container.Hgg_BR )
            print '  Acceptance:   ' + str( self.acceptance )
            print '  Total fid XS: ' + str( self.container.fid_XS(self.acceptance) )
            print

        # Final normalized values
        self.values = [ self.normalization * i for i in self.unnormalized_values ]


        # And the normalized histogram
        H.Scale( self.normalization )



        # --> Can't do this! other channel contributions would be scaled as well when changing kappas.
        #     Instead add after kappa scaling

        # # Add other channel contributions if these are set
        # if self.container.OC_filled:
        #     print 'Adding contributions from other channels as well'
        #     self.values = [ xs + OC_xs for xs, OC_xs in zip( self.values, self.container.OC_XS ) ]

        #     for i in xrange(self.n_pt_bins):
        #         H.SetBinContent( i+1, H.GetBinContent(i+1) + self.container.OC_XS[i] )



        # Deepcopy H into self.H to make sure histogram persists
        self.H = deepcopy( H )


        # Save histogram to .pickle to avoid constant redrawing
        with open( 'H_' + self.name + '.pickle', 'wb' ) as pickle_fp:
            pickle.dump( H, pickle_fp )




    def Set_values_from_pickle_file( self, pickle_file, Verbose = False ):

        with open( pickle_file, 'rb' ) as pickle_fp:
            self.H = pickle.load( pickle_fp )

        self.values = [ self.H.GetBinContent(i+1) for i in xrange(self.n_pt_bins) ]

        self.Set_values_from_histogram()





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


