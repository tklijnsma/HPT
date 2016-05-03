
from Spectrum import Spectrum
from Spectrum import Spectra_container


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

    # kg1_root_file = '../Run_gridpacks_and_shower/Saved_root_files/kg1_gg_H/Showered.root'
    # kt1_root_file = '../Run_gridpacks_and_shower/Saved_root_files/kt1_gg_H_quark-mass-effects/Showered.root'
    # analysis_level = 'SHOWERED'

    # kg1_root_file = '../Apply_flashgg/Saved_root_files/flashgg_kg1_gg_H.root'
    # kt1_root_file = '../Apply_flashgg/Saved_root_files/flashgg_kt1_gg_H_quark-mass-effects.root'
    kg1_root_file = '../Apply_flashgg/flashgg_kg1_gg_H.root'
    kt1_root_file = '../Apply_flashgg/flashgg_kt1_gg_H_quark-mass-effects.root'
    analysis_level = 'CUTS'

    # Initialize
    spec = Spectra_container( analysis_level )

    spec.Set_data_spectrum(
        bins = [ 0, 15, 26, 43, 72, 125, 200 ],
        values   = [ 9.0, 2.0, 3.4, 6.2, 4.6, 2.6, 0.7 ],
        err_up   = [ 6.4, 4.9, 4.8, 3.7, 2.4, 1.0, 0.5 ],
        err_down = [ -6.2, -5.5, -4.6, -3.5, -2.7, -1.0, -0.4 ],
        max_pt = 300.0,
        )

    if not args.redraw and os.path.isfile('H_kt1.pickle') and os.path.isfile('H_kg1.pickle'):
        # Load pickle files with histograms in there
        print 'Reading histograms from .pickle files'
        spec.kg1.Set_values_from_pickle_file( 'H_kg1.pickle' )
        spec.kt1.Set_values_from_pickle_file( 'H_kt1.pickle' )
    else:
        # Load both MC spectra from their root files (.Draw() command)
        spec.kg1.Set_values_from_root_file( kg1_root_file, Verbose=True )
        spec.kt1.Set_values_from_root_file( kt1_root_file, Verbose=True )

    spec.kg1.Print_H()
    spec.kt1.Print_H()

    Draw_both_unnormalized_spectra( spec )
    Draw_both_normalized_spectra( spec )



########################################
# Functions
########################################

def Draw_both_unnormalized_spectra( spec ):

    ROOT.gStyle.SetOptStat(0)

    spec.c1.Clear()

    # Convenience pointers
    kt1 = spec.kt1.H
    kg1 = spec.kg1.H

    kt1.Draw('LE1')
    kg1.Draw('LE1HISTSAME')

    kt1.SetTitle('Both p_{t} spectra (unnormalized)')
    kt1.GetXaxis().SetTitle( 'p_{t} [GeV]' )
    kt1.GetYaxis().SetTitle( 'Entries' )
    kt1.GetYaxis().SetTitleOffset(1.30)


    # Histogram drawing settings
    kt1.SetLineWidth(2)
    kg1.SetLineWidth(2)
    kg1.SetLineColor(2)

    # Set y-axis limit
    y_max = 1.1 * max( kt1.GetMaximum(), kg1.GetMaximum() )
    kt1.SetMaximum( y_max )

    # ======================================
    # Some information text boxes

    tl = ROOT.TLatex()
    tl.SetNDC()
    tl.SetTextSize(0.035)
    
    # Convenience variables: nl = next line, nc = next column
    nl = 0.05
    nc = 0.15
    lx = 0.64
    ly = 0.81

    tl.SetTextColor(1)
    tl.DrawLatex( lx, ly+nl, 'Total entries:' )    
    tl.SetTextColor(4)
    tl.DrawLatex( lx, ly, '#kappa_{t}=1, #kappa_{g}=0:' )
    tl.DrawLatex( lx+nc, ly, str(int(kt1.GetEntries())) )
    tl.SetTextColor(2)
    tl.DrawLatex( lx, ly-nl, '#kappa_{t}=0, #kappa_{g}=1:' )
    tl.DrawLatex( lx+nc, ly-nl, str(int(kg1.GetEntries())) )


    spec.c1.Print( 'Both_unnormalized_spectra.pdf', '.pdf' )

    ROOT.gStyle.SetOptStat(1011)


def Draw_both_normalized_spectra( spec ):

    ROOT.gStyle.SetOptStat(0)

    spec.c1.Clear()

    # Convenience pointers
    kt1 = spec.kt1.H
    kg1 = spec.kg1.H

    # Normalizes
    kt1.Scale( spec.kt1.normalization )
    kg1.Scale( spec.kg1.normalization )

    # # Make data histogram
    # data = ROOT.TH1F( 'data', 'data',
    #     spec.n_pt_bins,
    #     array( 'd', spec.pt_bins ),
    #     )

    # for i_val in range(spec.n_pt_bins):
    #     data.SetBinContent( i_val+1, spec.data.values[i_val] )

    # Purely visual minimal data shift
    data_shift = 2.0

    if not spec.data.err_up == []:
        data = ROOT.TGraphAsymmErrors(
            spec.n_pt_bins,
            array( 'd', [ kt1.GetBinCenter(i+1)+data_shift for i in range(spec.n_pt_bins) ] ),
            array( 'd', [ i for i in spec.data.values ] ),
            array( 'd', [ 0 for i in range(spec.n_pt_bins) ] ),
            array( 'd', [ 0 for i in range(spec.n_pt_bins) ] ),
            array( 'd', [ -i for i in spec.data.err_down ] ),
            array( 'd', spec.data.err_up ),
            )
    else:
        data = ROOT.TGraphAsymmErrors(
            spec.n_pt_bins,
            array( 'd', [ kt1.GetBinCenter(i+1) for i in range(spec.n_pt_bins) ] ),
            array( 'd', spec.data.values ),
            array( 'd', [ 0 for i in range(spec.n_pt_bins) ] ),
            array( 'd', [ 0 for i in range(spec.n_pt_bins) ] ),
            array( 'd', [ 0 for i in range(spec.n_pt_bins) ] ),
            array( 'd', [ 0 for i in range(spec.n_pt_bins) ] ),
            )

    kt1.Draw("LE1")
    kg1.Draw('LE1HISTSAME')
    data.Draw('PSAME')

    kt1.SetTitle('Both p_{t} spectra (normalized)')
    kt1.GetXaxis().SetTitle( 'p_{t} [GeV]' )
    kt1.GetYaxis().SetTitle( '#Delta#sigma [fb]' )
    kt1.GetYaxis().SetTitleOffset(1.30)

    # Histogram drawing settings
    kt1.SetLineWidth(2)
    kg1.SetLineWidth(2)
    kg1.SetLineColor(2)
    data.SetMarkerStyle(8)
    #data.SetLineWidth(2)
    data.SetMarkerColor(1)

    # Set y-axis limit
    y_max = 1.5 * max( kt1.GetMaximum(), kg1.GetMaximum() )
    kt1.SetMaximum( y_max )

    # ======================================
    # Some information text boxes

    tl = ROOT.TLatex()
    tl.SetNDC()
    tl.SetTextSize(0.035)
    
    # Convenience variables: nl = next line, nc = next column
    nl = 0.05
    nc = 0.15
    lx = 0.64
    ly = 0.81

    tl.SetTextColor(1)
    tl.DrawLatex( lx, ly+nl, 'Total cross section:' )
    tl.SetTextColor(4)
    tl.DrawLatex( lx, ly, '#kappa_{t}=1, #kappa_{g}=0:' )
    tl.DrawLatex( lx+nc, ly, '{0:.2f} fb'.format(kt1.Integral()) )
    tl.SetTextColor(2)
    tl.DrawLatex( lx, ly-nl, '#kappa_{t}=0, #kappa_{g}=1:' )
    tl.DrawLatex( lx+nc, ly-nl, '{0:.2f} fb'.format(kg1.Integral()) )
    tl.SetTextColor(1)
    tl.DrawLatex( lx, ly-2*nl, 'Data:' )
    tl.DrawLatex( lx+nc, ly-2*nl, '{0:.2f} fb'.format(sum(spec.data.values)) )


    spec.c1.Print( 'Both_normalized_spectra.pdf', '.pdf' )

    ROOT.gStyle.SetOptStat(1011)




########################################
# End of Main
########################################
if __name__ == "__main__":
    main()