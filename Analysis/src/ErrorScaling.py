from Spectrum import Spectra_container

from array import array
from math import pi, sqrt, exp, log
from copy import deepcopy

import os
import numpy

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kError;")
ROOT.RooMsgService.instance().setSilentMode(True)


def ErrorScaling( self ):

    n_points = len(self.data.values)
    n_bins   = n_points


    # Read cross sections into lists

    s_data          = self.data.values[:]
    s_data_err_up   = self.data.err_up[:]
    s_data_err_down = self.data.err_down[:]
    s_data_err_symm = [ 0.5*(abs(i)+abs(j)) for i, j in zip( s_data_err_up, s_data_err_down ) ]

    s_kt1 = self.kt1.values[:]
    s_kg1 = self.kg1.values[:]


    # ----------------------------
    # For now:
    # Take the errors on data as errors on the kt == 1 spectrum
    # Spectrum + uncertainties should later be done by throwing toys

    if self.OC_filled:
        s_exp      = [ s_kt + s_OC for s_kt, s_OC in zip( self.kt1.values, self.OC_XS ) ]
    else:
        s_exp      = self.kt1.values

    s_exp_err_up   = self.data.err_up[:]
    s_exp_err_down = self.data.err_down[:]
    s_exp_err_symm = [ 0.5*(abs(i)+abs(j)) for i, j in zip( s_exp_err_up, s_exp_err_down ) ]


    # ----------------------------
    # Error scaling

    original_lumi = 19.7  # fb^-1
    target_lumi   = 800.0


    scaling = sqrt(original_lumi / target_lumi)

    multiply_list = lambda some_list, factor: [ factor*i for i in some_list ]
    s_exp_err_up   = multiply_list( s_exp_err_up,   scaling )
    s_exp_err_down = multiply_list( s_exp_err_down, scaling )
    s_exp_err_symm = multiply_list( s_exp_err_symm, scaling )


    ########################################
    # Open a canvas and draw a base
    ########################################

    if not hasattr( self, 'c' ):
        self.c = ROOT.TCanvas( 'c', 'c', 1000, 700 )
    else:
        self.c.Clear()

    BottomMargin = 0.15
    LeftMargin   = 0.18
    TopMargin    = 0.06
    RightMargin  = 0.04

    self.c.SetBottomMargin( BottomMargin )
    self.c.SetLeftMargin(   LeftMargin )
    self.c.SetTopMargin(    TopMargin )
    self.c.SetRightMargin(  RightMargin )

    y_marg = 1.0 - RightMargin - LeftMargin
    x_marg = 1.0 - TopMargin - BottomMargin

    h = 700
    w = int(h / y_marg * x_marg)

    self.c.SetCanvasSize( w, h )
    self.c.SetLogy()
    self.c.SetGrid()


    x_min = 0.0
    x_max = self.data.pt_bins[-1]
    y_min = max( 0.5*min([ val-abs(err) for val, err in zip( s_exp, s_exp_err_down ) ]), 0.0001 )
    y_max = 1.1*max([ val+err for val, err in zip( s_exp, s_exp_err_up ) ])


    # base owns the axes
    base = ROOT.TH1F()
    base.SetTitle('')

    base.SetMinimum( y_min )
    base.SetMaximum( y_max )
    base.GetXaxis().SetLimits( x_min, x_max )

    base.GetXaxis().SetTitle('p_{t} [GeV]')
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


    ########################################
    # 2
    ########################################

    TG_exp = ROOT.TGraphAsymmErrors(
        n_bins,
        array( 'f', self.data.bin_centers ),
        array( 'f', s_exp ),
        array( 'f', self.data.half_bin_widths ),
        array( 'f', self.data.half_bin_widths ),
        array( 'f', [ abs(s) for s in s_exp_err_down ] ),
        array( 'f', s_exp_err_up ),
        )

    TG_exp.SetLineWidth(2)
    TG_exp.SetMarkerStyle(8)
    TG_exp.SetName( 'expected' )

    TG_exp.Draw('PE1SAME')



    ########################################
    # Labels and legend
    ########################################

    leg_width  = 0.4
    leg_height = 0.1
    legend = ROOT.TLegend( 1.0-RightMargin-leg_width, 1.0-TopMargin-leg_height, 1.0-RightMargin, 1.0-TopMargin )
    legend.AddEntry( 'expected', 'Expected XS', 'lpe' )

    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.Draw('SAME')



    lumi_label = ROOT.TLatex()
    lumi_label.SetNDC()
    lumi_label.SetTextSize(0.045)
    lumi_label.SetTextAlign(31)
    lumi_label.DrawLatex( 1.0-RightMargin+0.005, 1.0-TopMargin+0.005, 'L = {0:.1f} fb^{{-1}}'.format(target_lumi) )

    # Not the most useful plot
    # self.c.SaveAs( os.path.join( self.plotdir, 'ErrorScaling.pdf' ) )





    ########################################
    # Rerun the kappa fit
    ########################################

    print 'Rerunning kappa fit with pseudodata'

    # Make a pseudodata spectrum - copy the data spectrum and replace the values

    # Deepcopying is a bit of a pain, since there is a reference to the parent object
    # First remove container, then add it back in later
    del self.data.container

    # Backup the original data spectrum
    data_backup = deepcopy( self.data )
    data_backup.container = self

    # Overwrite lists with the pseudo data
    self.data.values   = s_exp
    self.data.err_up   = s_exp_err_up
    self.data.err_down = s_exp_err_down
    self.data.raw_sum  = sum([ val * width for val, width in zip( self.data.values, self.data.bin_widths ) ])
    self.data.container = self


    plot_appendix = '_pseudodata{0:.0f}'.format(target_lumi)

    # Run with the pseudodata
    self.kappa_plot( plot_appendix = plot_appendix, luminosity = target_lumi )

    # Redraw the spectra
    self.Draw_both_normalized_spectra( plot_appendix = plot_appendix, luminosity=target_lumi )



    # Put back the original data spectrum
    self.data = data_backup




Spectra_container.ErrorScaling = ErrorScaling