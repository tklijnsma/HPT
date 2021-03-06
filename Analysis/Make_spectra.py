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

    kg1_root_file = '../Apply_flashgg/Saved_root_files/9May/flashgg_0509_kg1_ren_gg_H.root'
    kt1_root_file = '../Apply_flashgg/Saved_root_files/9May/flashgg_0508_kt1_gg_H_quark-mass-effects.root'    

    analysis_level = 'CUTS'


    massCut = 100.
    ptLeadCut = 1./3.
    ptSubleadCut = 1./4.

    # Currently only the mass cut
    cuts = [

        #'abs(mass-125.)<0.2'

        'mass > {0}'.format(massCut),
        
        'leadPt > {0:.2f}*mass && subLeadPt > {1:.2f}*mass'.format(
            ptLeadCut, ptSubleadCut ),
        
        'leadExtraGenIso < 10. && subLeadExtraGenIso < 10.',
        
        ( '(abs(leadEta)    < 2.5    && abs(subLeadEta) < 2.5  )'
          '&& (abs(leadEta)    < 1.4442 || abs(leadEta)    > 1.566)'
          '&& (abs(subLeadEta) < 1.4442 || abs(subLeadEta) > 1.566)'
          ),

        ]

    # Initialize
    spec = Spectra_container( analysis_level, cuts )

    spec.Set_data_spectrum(
        bins     = [ 0, 15, 26, 43, 72, 125, 200 ],
        values   = [ 9.0, 2.0, 3.4, 6.2, 4.6, 2.6, 0.7 ],
        err_up   = [ 6.4, 4.9, 4.8, 3.7, 2.4, 1.0, 0.5 ],
        err_down = [ -6.2, -5.5, -4.6, -3.5, -2.7, -1.0, -0.4 ],
        max_pt   = 300.0,
        )

    # Read the root file to get contributions from VBF, ...
    spec.Get_other_channel_contributions()

    if not args.redraw and os.path.isfile('H_kt1.pickle') and os.path.isfile('H_kg1.pickle'):
        # Load pickle files with histograms in there
        print 'Reading histograms from .pickle files'
        spec.kg1.Set_values_from_pickle_file( 'H_kg1.pickle' )
        spec.kt1.Set_values_from_pickle_file( 'H_kt1.pickle' )
    else:
        # Load both MC spectra from their root files (.Draw() command)
        spec.kg1.Set_values_from_root_file( kg1_root_file, Verbose=True )
        spec.kt1.Set_values_from_root_file( kt1_root_file, Verbose=True )

    # spec.kg1.Print_H()
    # spec.kt1.Print_H()


    spec.Quadratic_fit()

    print '\n' + '#'*70
    print 'Kappa plot\n'
    spec.kappa_plot()


    print '\n' + '#'*70
    print 'Making plots\n'

    # spec.Plot_quadratic_fit()

    print 'Plotting the different spectra'
    spec.Draw_both_normalized_spectra()

    print '\n' + '#'*70
    print 'Error scaling\n'
    spec.ErrorScaling()



########################################
# Functions
########################################




########################################
# End of Main
########################################
if __name__ == "__main__":
    main()