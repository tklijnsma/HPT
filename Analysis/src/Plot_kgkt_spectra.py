from Spectrum import Spectrum
from Spectrum import Spectra_container

import ROOT
ROOT.gStyle.SetOptStat(0)


import os

from array import array



def Draw_both_normalized_spectra( self, draw_data=True, log_scale=True, plot_appendix='', luminosity=19.7 ):

    ROOT.gStyle.SetOptStat(0)


    # ======================================
    # Canvas and base settings

    self.c1.Clear()
    self.c1.SetLogy(False)

    BottomMargin = 0.15
    LeftMargin   = 0.18
    TopMargin    = 0.06
    RightMargin  = 0.04

    self.c1.SetBottomMargin( BottomMargin )
    self.c1.SetLeftMargin(   LeftMargin )
    self.c1.SetTopMargin(    TopMargin )
    self.c1.SetRightMargin(  RightMargin )

    y_marg = 1.0 - RightMargin - LeftMargin
    x_marg = 1.0 - TopMargin - BottomMargin

    h = 700
    w = int(h / y_marg * x_marg)

    self.c1.SetCanvasSize( w, h )
    self.c1.SetGrid()

    x_min = 0.0
    x_max = self.data.pt_bins[-1]

    # base owns the axes
    base = ROOT.TH1F()
    base.SetTitle('')

    base.GetXaxis().SetLimits( x_min, x_max )

    x_title = self.vartitle + self.varunit
    base.GetXaxis().SetTitle(x_title)
    base.GetXaxis().SetTitleSize(0.065)
    base.GetXaxis().SetTitleOffset(1.0)
    base.GetXaxis().SetLabelSize(0.05)
    # base.GetXaxis().SetNdivisions(505)
    
    base.GetYaxis().SetTitle('#Delta#sigma/#Delta p_{t} [fb/GeV]')
    base.GetYaxis().SetTitleSize(0.065)
    base.GetYaxis().SetTitleOffset(1.25)
    base.GetYaxis().SetLabelSize(0.05)
    # base.GetYaxis().SetNdivisions(505)

    # base.GetZaxis().SetRangeUser( 0., 1. )

    base.Draw('P')


    # ======================================
    # Graph objects

    # Clone the histograms of the kt1 and kg1 spectra
    kt1 = self.kt1.H.Clone()
    kg1 = self.kg1.H.Clone()

    # Add other channel contributions
    if self.OC_filled:
        for i_bin in xrange(self.n_pt_bins):
            kt1.SetBinContent( i_bin+1, kt1.GetBinContent(i_bin+1) + self.OC_XS[i_bin] )
            kg1.SetBinContent( i_bin+1, kg1.GetBinContent(i_bin+1) + self.OC_XS[i_bin] )


    if draw_data:
        # Create the TGraph for the data points (errors may be symmetrized)
        if hasattr( self.data, 'err_up' ):
            data = ROOT.TGraphAsymmErrors(
                self.n_pt_bins,
                array( 'd', [ kt1.GetBinCenter(i+1) for i in range(self.n_pt_bins) ] ),
                array( 'd', [ i for i in self.data.values ] ),
                array( 'd', [ 0 for i in range(self.n_pt_bins) ] ),
                array( 'd', [ 0 for i in range(self.n_pt_bins) ] ),
                array( 'd', [ abs(i) for i in self.data.err_down ] ), # Enforce positive error
                array( 'd', self.data.err_up ),
                )
        else:
            data = ROOT.TGraphAsymmErrors(
                self.n_pt_bins,
                array( 'd', [ kt1.GetBinCenter(i+1) for i in range(self.n_pt_bins) ] ),
                array( 'd', self.data.values ),
                array( 'd', [ 0 for i in range(self.n_pt_bins) ] ),
                array( 'd', [ 0 for i in range(self.n_pt_bins) ] ),
                array( 'd', [ 0 for i in range(self.n_pt_bins) ] ),
                array( 'd', [ 0 for i in range(self.n_pt_bins) ] ),
                )



    kt1.Draw("LE1HISTSAME")
    kg1.Draw('LE1HISTSAME')
    if draw_data: data.Draw('PSAME')


    # Draw the best fit if it's available
    if hasattr( self, 'best_fit' ) and draw_data:
        H_bestfit = self.kt1.H.Clone('bestfit')
        for i_bin in xrange(self.n_pt_bins):
            H_bestfit.SetBinContent( i_bin+1, self.best_fit[i_bin] )
        H_bestfit.Draw('LE1HISTSAME')
        H_bestfit.SetLineColor(3)
        H_bestfit.SetLineWidth(4)
        H_bestfit.SetLineStyle(2)


    kt1.SetTitle('Both p_{t} spectra (normalized)')
    kt1.GetXaxis().SetTitle( 'p_{t} [GeV]' )
    kt1.GetYaxis().SetTitle( '#Delta#sigma [fb]' )
    kt1.GetYaxis().SetTitleOffset(1.30)

    # Histogram drawing settings
    kt1.SetLineWidth(2)
    kg1.SetLineWidth(2)
    kg1.SetLineColor(2)

    if draw_data:
        data.SetMarkerStyle(8)
        #data.SetLineWidth(2)
        data.SetMarkerColor(1)

    # Set y-axis limits
    
    if not draw_data:

        untreated_y_max = max( kt1.GetMaximum(), kg1.GetMaximum() )
        untreated_y_min = min( kt1.GetMinimum(), kg1.GetMinimum() )

    elif hasattr( self.kt1, 'err_up' ):
        untreated_y_max = max(
            [ val + err for val, err in zip( self.kt1.values, self.kt1.err_up ) ] +
            [ val + err for val, err in zip( self.kg1.values, self.kg1.err_up ) ] +
            [ val + err for val, err in zip( self.data.values, self.data.err_up ) ] )

        untreated_y_min = min(
            [ val - abs(err) for val, err in zip( self.kt1.values, self.kt1.err_down ) ] +
            [ val - abs(err) for val, err in zip( self.kg1.values, self.kg1.err_down ) ] +
            [ val - abs(err) for val, err in zip( self.data.values, self.data.err_down ) ] )
    else:
        untreated_y_max = max(
            self.kt1.values +
            self.kg1.values +
            [ val + err for val, err in zip( self.data.values, self.data.err_up ) ]  )

        untreated_y_min = min(
            self.kt1.values +
            self.kg1.values +
            [ val - abs(err) for val, err in zip( self.data.values, self.data.err_down ) ] )


    if log_scale:
        self.c1.SetLogy()
        y_min = max( 0.0001, 0.5 * untreated_y_min )
        y_max = 1.1 * untreated_y_max
    
    else:

        if untreated_y_min < 0:
            y_min = 1.1 * untreated_y_min
        else:
            y_min = 0.9 * untreated_y_min

        y_max = 1.1 * untreated_y_max


    base.SetMaximum( y_max )
    base.SetMinimum( y_min )


    # ======================================
    # Some information text boxes

    tl = ROOT.TLatex()
    tl.SetNDC()
    tl.SetTextSize(0.035)
    tl.SetTextAlign(13)
    
    # Convenience variables: nl = next line, nc = next column
    nl = 0.05
    nc = 0.27
    lx = 0.55
    ly = 1.0 - TopMargin - 0.07

    tl.SetTextColor(1)
    tl.DrawLatex( lx, ly+nl, 'Total cross section:' )
    tl.SetTextColor(4)
    tl.DrawLatex( lx, ly, '#kappa_{t}=1, #kappa_{g}=0:' )
    tl.DrawLatex( lx+nc, ly, '{0:.2f} fb'.format(kt1.Integral('width')) )
    tl.SetTextColor(2)
    tl.DrawLatex( lx, ly-nl, '#kappa_{t}=0, #kappa_{g}=1:' )
    tl.DrawLatex( lx+nc, ly-nl, '{0:.2f} fb'.format(kg1.Integral('width')) )
    tl.SetTextColor(1)
    tl.DrawLatex( lx, ly-2*nl, 'Data:' )
    tl.DrawLatex( lx+nc, ly-2*nl, '{0:.2f} fb'.format(self.data.raw_sum) )

    if hasattr( self, 'best_fit' ):

        display_str = '#kappa_{{t}}={0:.2f}, #kappa_{{g}}={1:.2f}:'.format( self.kt_minimum, self.kg_minimum )
        bestfit_sum = sum([ xs * width for xs, width in zip( self.best_fit, self.data.bin_widths ) ])

        tl.SetTextColor(3)
        tl.DrawLatex( lx, ly-3*nl, display_str )
        tl.DrawLatex( lx+nc, ly-3*nl, '{0:.2f} fb'.format(bestfit_sum) )


    lumi_label = ROOT.TLatex()
    lumi_label.SetNDC()
    lumi_label.SetTextSize(0.045)
    lumi_label.SetTextAlign(31)
    lumi_label.DrawLatex( 1.0-RightMargin+0.005, 1.0-TopMargin+0.005, 'L = {0:.1f} fb^{{-1}}'.format(luminosity) )



    outfilename = 'Both_normalized_spectra' + plot_appendix + '.pdf'

    if not os.path.isdir(self.plotdir): os.makedirs(self.plotdir)
    self.c1.SaveAs( os.path.join( self.plotdir, outfilename ) )



Spectra_container.Draw_both_normalized_spectra = Draw_both_normalized_spectra