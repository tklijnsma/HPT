from Spectrum import Spectrum
from Spectrum import Spectra_container

import ROOT
import os

from array import array


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
    data_shift = 3.0

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
    y_max = 2.0 * max( kt1.GetMaximum(), kg1.GetMaximum() )
    kt1.SetMaximum( y_max )
    kt1.SetMinimum( -1.0 )

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
