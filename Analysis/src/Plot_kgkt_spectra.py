from Spectrum import Spectrum
from Spectrum import Spectra_container

import ROOT
import os

from array import array


def Draw_both_unnormalized_spectra( spec,
    out_filename = 'Both_unnormalized_spectra',
    also_png = False,
    ):

    ROOT.gStyle.SetOptStat(0)

    spec.c1.Clear()

    spec.c1.SetLogy()

    # Convenience pointers
    kt1 = spec.kt1.H
    kg1 = spec.kg1.H

    for i in range( spec.n_pt_bins ):

        kt1.SetBinContent( i+1, kt1.GetBinContent(i+1) / kt1.GetXaxis().GetBinWidth(i+1) )
        kg1.SetBinContent( i+1, kg1.GetBinContent(i+1) / kg1.GetXaxis().GetBinWidth(i+1) )

        kt1.SetBinError( i+1, kt1.GetBinError(i+1) / kt1.GetXaxis().GetBinWidth(i+1) )
        kg1.SetBinError( i+1, kg1.GetBinError(i+1) / kg1.GetXaxis().GetBinWidth(i+1) )



    kt1.Draw('LE1')
    kg1.Draw('LE1HISTSAME')

    kt1.SetTitle('Both p_{t} spectra (unnormalized)')
    kt1.GetYaxis().SetTitle( '#Delta #sigma / #Delta p_{t} [AU]' )
    kt1.GetXaxis().SetTitle( 'p_{t} [GeV]' )
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


    spec.c1.Print( out_filename + '.pdf', '.pdf' )

    if also_png:
        spec.c1.Print( out_filename + '.png', '.png' )

    ROOT.gStyle.SetOptStat(1011)


def Draw_both_normalized_spectra( spec ):

    ROOT.gStyle.SetOptStat(0)

    spec.c1.Clear()

    # Convenience pointers
    kt1 = spec.kt1.norm_H
    kg1 = spec.kg1.norm_H

    # Normalizes
    # kt1.Scale( spec.kt1.normalization )
    # kg1.Scale( spec.kg1.normalization )
    # kt1.Scale( kt1.Integral() )
    # kg1.Scale( ktg.Integral() )


    # # Make data histogram
    # data = ROOT.TH1F( 'data', 'data',
    #     spec.n_pt_bins,
    #     array( 'd', spec.pt_bins ),
    #     )

    # for i_val in range(spec.n_pt_bins):
    #     data.SetBinContent( i_val+1, spec.data.values[i_val] )

    # Purely visual minimal data shift
    data_shift = 0.0

    if not spec.data.err_up == []:
        data = ROOT.TGraphAsymmErrors(
            spec.n_pt_bins,
            array( 'd', [ kt1.GetBinCenter(i+1)+data_shift for i in range(spec.n_pt_bins) ] ),
            array( 'd', [ i for i in spec.data.norm_values ] ),
            array( 'd', [ 0 for i in range(spec.n_pt_bins) ] ),
            array( 'd', [ 0 for i in range(spec.n_pt_bins) ] ),
            array( 'd', [ -i for i in spec.data.norm_err_down ] ),
            array( 'd', spec.data.norm_err_up ),
            )
    else:
        data = ROOT.TGraphAsymmErrors(
            spec.n_pt_bins,
            array( 'd', [ kt1.GetBinCenter(i+1) for i in range(spec.n_pt_bins) ] ),
            array( 'd', spec.data.norm_values ),
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

    # # Set y-axis limit
    y_max = 1.1 * max(
        [ val + err for val, err in zip( spec.kt1.norm_values, spec.kt1.norm_err_up ) ] +
        [ val + err for val, err in zip( spec.kg1.norm_values, spec.kg1.norm_err_up ) ] +
        [ val + err for val, err in zip( spec.data.norm_values, spec.data.norm_err_up ) ] )

    y_min = 0.5 * min(
        [ val - abs(err) for val, err in zip( spec.kt1.norm_values, spec.kt1.norm_err_down ) ] +
        [ val - abs(err) for val, err in zip( spec.kg1.norm_values, spec.kg1.norm_err_down ) ] +
        [ val - abs(err) for val, err in zip( spec.data.norm_values, spec.data.norm_err_down ) ] )

    kt1.SetMaximum( y_max )
    kt1.SetMinimum( max( y_min, 0.001 ) )

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
    tl.DrawLatex( lx+nc, ly-2*nl, '{0:.2f} fb'.format(sum(spec.data.norm_values)) )


    spec.c1.Print( 'Both_normalized_spectra.pdf', '.pdf' )

    ROOT.gStyle.SetOptStat(1011)
