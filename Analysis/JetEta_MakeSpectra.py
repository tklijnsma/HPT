import sys
sys.path.append('src')

from Spectrum import Spectrum
from Spectrum import Spectra_container

import Plot_kgkt_spectra
import kappa_elips
import ErrorScaling
import Quadratic_fit

import ROOT
import argparse
import os

from array import array


########################################
# Main
########################################

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument( '--redraw', action='store_true', help='Forces the program to redraw the histograms from the root files')
    args = parser.parse_args()


    # ======================================
    # Set up ROOT

    print 'Importing root libraries'
    ROOT.gSystem.Load("libDataFormatsFWLite.so")
    ROOT.AutoLibraryLoader.enable()
    #ROOT.FWLiteEnabler.enable()

    ROOT.gROOT.SetBatch(True)
    ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kError;")
    #ROOT.gStyle.SetOptFit(1011)


    # ======================================
    # Set up spectrum class

    kg1_root_file = '../Apply_flashgg/Saved_root_files/20Sep/flashgg_0812_kg1_gg_H.root'
    kt1_root_file = '../Apply_flashgg/Saved_root_files/20Sep/flashgg_0812_kt1_gg_H_quark-mass-effects.root'

    # Can also be "SHOWERED", which instructs to read root files before flashgg (pure Pythia output)
    analysis_level = 'CUTS'

    # Kinematic cuts
    massCut = 100.
    ptLeadCut = 1./3.
    ptSubleadCut = 1./4.

    # Currently only the mass cut
    cuts = [

        # Only look at events with 1 or more jet (excluding the 2 gamma jets)
        'nJets4p7 > 0',

        # Standard kinematic cuts
        'mass > {0}'.format(massCut),
        
        'leadPt > {0:.2f}*mass && subLeadPt > {1:.2f}*mass'.format(
            ptLeadCut, ptSubleadCut ),
        
        'leadExtraGenIso < 10. && subLeadExtraGenIso < 10.',
        
        (
            '(abs(leadEta)    < 2.5    && abs(subLeadEta) < 2.5  )'
            '&& (abs(leadEta)    < 1.4442 || abs(leadEta)    > 1.566)'
            '&& (abs(subLeadEta) < 1.4442 || abs(subLeadEta) > 1.566)'
            ),

        # Additional pt-cut: NO DATA AVAILABLE FOR THIS
        'pt > 100'

        ]

    # Initialize
    spec = Spectra_container( analysis_level, cuts )

    # Change plot dir so old plots are not overwritten
    spec.plotdir = 'plots_JetEta'

    spec.vartitle = '|y^{#gamma#gamma}-y^{j1}|'
    spec.varunit  = ''

    # gg_eta - jet_eta spectrum
    spec.Set_data_spectrum(
        bins     = [ 0.0, 0.62, 1.25, 1.92 ],
        values   = [ 6.1, -1.1, 5.2, 1.6 ],
        err_up   = [ 4.0, 4.4, 3.0, 4.1 ],
        err_down = [ 3.8, 3.6, 2.8, 4.8 ],
        max_pt   = 2.2,
        )

    # Read the root file to get contributions from VBF, ...
    # spec.Get_other_channel_contributions()

    # >>>> Not yet done for jetEta !
    # For now, just guess the other contributions from the paper plot
    # spec.OC_XS = [ 1.5, 1.25, 0.95, 0.7 ]
    # spec.OC_filled = True


    # Load both MC spectra from their root files (.Draw() command)
    varname = 'abs(rapidity-jet0Rapidity)'
    # varname = 'abs(abs(rapidity)-abs(jet0Rapidity))'
    spec.kg1.Set_values_from_root_file( kg1_root_file, varname=varname, Verbose=True )
    spec.kt1.Set_values_from_root_file( kt1_root_file, varname=varname, Verbose=True )


    spec.kg1.Print_H()
    spec.kt1.Print_H()


    # spec.Quadratic_fit()

    # print '\n' + '#'*70
    # print 'Kappa plot\n'
    # spec.kappa_plot()


    # print '\n' + '#'*70
    # print 'Making plots\n'

    # spec.Plot_quadratic_fit()

    print 'Plotting the different spectra'
    spec.Draw_both_normalized_spectra( draw_data=False, log_scale=False )

    # print '\n' + '#'*70
    # print 'Error scaling\n'
    # spec.ErrorScaling()



########################################
# Functions
########################################




########################################
# End of Main
########################################
if __name__ == "__main__":
    main()