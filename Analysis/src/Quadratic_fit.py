from Spectrum import Spectrum
from Spectrum import Spectra_container

import ROOT
import os
from math import sqrt

from array import array
from copy import deepcopy


def Quadratic_fit( spec ):

    # Convenience pointers
    kt1 = spec.kt1.H
    kg1 = spec.kg1.H


    # Define:
    #  sigma  =  | alpha * kappa_g  +  beta * kappa_t |^2

    # then
    #  alpha / beta  =  sqrt( sigma_i / sigma_j )
    #  beta / alpha  =  sqrt( sigma_j / sigma_i )

    spec.ratios = []

    for i in range(spec.n_pt_bins):

        alpha_over_beta = sqrt(spec.kg1.unnormalized_values[i] / spec.kt1.unnormalized_values[i])
        beta_over_alpha = sqrt(spec.kt1.unnormalized_values[i] / spec.kg1.unnormalized_values[i])

        spec.ratios.append( beta_over_alpha )


    print 'Ratios sigma_{kt-sample} over sigma_{kg-sample}:'

    for i in range(spec.n_pt_bins):

        print '    bin {0:2} | pt: {1:<4} to {2:<4} GeV | beta over alpha: {3}'.format(
            i,
            int(spec.pt_bins[i]),
            int(spec.pt_bins[i+1]),
            spec.ratios[i]
            )


def Plot_quadratic_fit( spec ):

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetLabelSize( 0.100, 'xy')

    spec.c1.Clear()
    spec.c1.SetLogy(0)
    spec.c1.SetGrid( 0, 0 )
    spec.c1.SetCanvasSize( 1000, 300 )

    H_ratio = ROOT.TH1F(
        'Ratio_hist',
        '', # Title
        spec.n_pt_bins,
        array( 'd', spec.pt_bins )
        )

    for i_bin in range(spec.n_pt_bins):
        H_ratio.SetBinContent( i_bin+1, spec.ratios[i_bin] )

    H_ratio.Draw('P')

    H_ratio.SetMarkerStyle(8)
    H_ratio.SetMarkerColor(8)
    H_ratio.SetMarkerSize(2)

    y_min =  0.8 * min(spec.ratios)
    y_max =  1.2 * max(spec.ratios)
    H_ratio.SetMaximum( y_max )
    H_ratio.SetMinimum( y_min )

    lines = []
    for i_bin in range(spec.n_pt_bins):
        lines.append(
            Line( spec.pt_bins[i_bin], y_min, spec.pt_bins[i_bin], y_max ) )
        lines[-1].Draw('LSAME')

    one_line = Line( 0.0, 1.0, spec.pt_bins[-1], 1.0 )
    one_line.SetLineStyle(1)
    one_line.SetLineWidth(2)
    one_line.Draw('LSAME')

    # H_ratio.GetXaxis().SetTitle( 'p_{t} [GeV]')
    # H_ratio.GetYaxis().SetTitle( '#beta / #alpha')

    spec.c1.Print( 'Ratio_plot.pdf', '.pdf' )


def Line( x1, y1, x2, y2 ):
    line = ROOT.TLine( x1, y1, x2, y2 )
    line.SetLineStyle(2)
    line.SetLineColor(15)
    line.SetLineWidth(1)
    return deepcopy( line )

