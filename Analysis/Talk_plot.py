import ROOT
import argparse
import os

from array import array


########################################
# Main
########################################

def main():

    # parser = argparse.ArgumentParser()
    # parser.add_argument( '--redraw', action='store_true', help='Forces the program to redraw the histograms from the root files')
    # args = parser.parse_args()


    # ======================================
    # Set up ROOT

    print 'Importing root libraries'
    ROOT.gSystem.Load("libDataFormatsFWLite.so")
    ROOT.AutoLibraryLoader.enable()
    #ROOT.FWLiteEnabler.enable()

    ROOT.gROOT.SetBatch(True)
    ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kError;")
    #ROOT.gStyle.SetOptFit(1011)

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetLabelSize( 0.100, 'xy')

    c1 = ROOT.TCanvas("c1","c1",1000,800)

    Plot_mus( c1 )





def Plot_mus( c1 ):

    c1.Clear()
    c1.SetGrid( 0, 0 )
    c1.SetCanvasSize( 1000, 300 )

    n_bins = 7
    pt_bins = [ 0, 15, 26, 43, 72, 125, 200, 300 ]

    pt_center = []
    pt_down = []
    pt_up = []
    for i in range(n_bins):
        half_bin_width = ( pt_bins[i+1] - pt_bins[i] ) /2.0 
        
        pt_center.append( pt_bins[i] + half_bin_width )
        pt_down.append( half_bin_width )
        pt_up.append( half_bin_width )

    # H_WW = H_gg.Clone( 'WW_hist' )
    # H_ZZ = H_gg.Clone( 'ZZ_hist' )

    mus = [ 1.0465, 0.3030, 0.5484, 1.2157, 1.3939, 2.0000, 1.1667, ]
    up =   [ .7442, .7424, .7742, .7255, .7273, .7692, .8333, ]
    down = [ -0.7209, -0.8333, -0.7419, -0.6863, -0.8182, -0.7692, -0.6667, ]

    T = ROOT.TGraphAsymmErrors(
        n_bins,
        array( 'd', pt_center ),
        array( 'd', mus ),
        array( 'd', pt_down ),
        array( 'd', pt_up ),
        array( 'd', [ -i for i in down ] ),
        array( 'd', up ),
        )
    T.Draw('AP')


    # for i_bin in range(n_bins):
    #     H_ratio.SetBinContent( i_bin+1, ratios[i_bin] )

    # H_ratio.Draw('P')

    # H_ratio.SetMarkerStyle(8)
    # H_ratio.SetMarkerColor(8)
    # H_ratio.SetMarkerSize(2)

    # y_min =  0.8 * min(ratios)
    # y_max =  1.2 * max(ratios)
    # H_ratio.SetMaximum( y_max )
    # H_ratio.SetMinimum( y_min )

    # lines = []
    # for i_bin in range(n_bins):
    #     lines.append(
    #         Line( pt_bins[i_bin], y_min, pt_bins[i_bin], y_max ) )
    #     lines[-1].Draw('LSAME')

    # one_line = Line( 0.0, 1.0, pt_bins[-1], 1.0 )
    # one_line.SetLineStyle(1)
    # one_line.SetLineWidth(2)
    # one_line.Draw('LSAME')

    # # H_ratio.GetXaxis().SetTitle( 'p_{t} [GeV]')
    # # H_ratio.GetYaxis().SetTitle( '#beta / #alpha')

    c1.Print( 'mu_plot.pdf', '.pdf' )


def Line( x1, y1, x2, y2 ):
    line = ROOT.TLine( x1, y1, x2, y2 )
    line.SetLineStyle(2)
    line.SetLineColor(15)
    line.SetLineWidth(1)
    return deepcopy( line )





########################################
# End of Main
########################################
if __name__ == "__main__":
    main()