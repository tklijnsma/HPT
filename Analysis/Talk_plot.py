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
    #ROOT.gStyle.SetLabelSize( 0.100, 'xy')

    c1 = ROOT.TCanvas("c1","c1",1000,800)

    Plot_mus( c1 )





def Plot_mus( c1 ):

    c1.Clear()
    c1.SetGrid( 0, 0 )
    c1.SetCanvasSize( 1000, 800 )


    bins_gg  = [ 0, 15, 26, 43, 72, 125, 200, 300 ]
    mus_gg   = [ 1.0465, 0.3030, 0.5484, 1.2157, 1.3939, 2.0000, 1.1667, ]
    up_gg    = [ .7442, .7424, .7742, .7255, .7273, .7692, .8333, ]
    down_gg  = [ 0.7209, 0.8333, 0.7419, 0.6863, 0.8182, 0.7692, 0.6667, ]

    bins_WW  = [ 0, 15, 45, 85, 125, 165, 300 ]
    mus_WW   = [ 0.792, 0.884, 0.972, 0.840, 0.714, 1.643, ]
    up_WW    = [ 0.476, 0.331, 0.380, 0.450, 0.529, 1.584, ]
    down_WW  = [ 0.395, 0.247, 0.353, 0.450, 0.503, 1.584, ]

    bins_ZZ  = [ 0, 15, 30, 60, 200 ]
    mus_ZZ   = [ 0.626, 1.100, 1.444, 1.111,  ]
    up_ZZ    = [ 0.641, 0.845, 0.913, 0.785,  ]
    down_ZZ  = [ 0.474, 0.558, 0.669, 0.538,  ]

    datasets = [
        ( 'gg', bins_gg, mus_gg, up_gg, down_gg, 2 ),
        ( 'WW', bins_WW, mus_WW, up_WW, down_WW, 3 ),
        ( 'ZZ', bins_ZZ, mus_ZZ, up_ZZ, down_ZZ, 4 ),
        ]


    ########################################
    # Setup base
    ########################################

    # Calculate ranges
    x_min = float(min( bins_gg + bins_WW + bins_ZZ ))
    x_max = float(max( bins_gg + bins_WW + bins_ZZ ))

    L_sub = lambda L, Lm: [ i - j for i,j in zip(L, Lm) ]
    L_add = lambda L, Lp: [ i + j for i,j in zip(L, Lp) ]
    y_min = min( L_sub( mus_gg, down_gg ) + L_sub( mus_WW, down_WW ) + L_sub( mus_ZZ, down_ZZ ) )
    y_max = max( L_add( mus_gg, down_gg ) + L_add( mus_WW, down_WW ) + L_add( mus_ZZ, down_ZZ ) )
    
    if y_min < 0.0:
        y_min *= 1.15
    else:
        y_min *= 0.85

    y_max *= 1.05

    print 'Ranges: x = ( {0} to {1} )  /  y = ( {2} to {3} )'.format( x_min, x_max, y_min, y_max )

    base = ROOT.TH1D( 'base', '', 1, x_min, x_max )
    base.SetBinContent( 1, -1000 )
    base.Draw('P')
    base.SetMinimum( y_min ); base.SetMaximum( y_max )

    base.GetXaxis().SetTitle( 'p_{t} [GeV]')
    base.GetYaxis().SetTitle( '#Delta #sigma / #Delta #sigma_{SM}' )


    ########################################
    # Plot the Tgraphs
    ########################################

    Ts = []
    for name, bins, mus, up, down, color in datasets:

        n_bins = len(bins) - 1

        centers = []
        left    = []
        right   = []
        for i in range(n_bins):
            half_bin_width = ( bins[i+1] - bins[i] ) /2.0 
            
            centers.append( bins[i] + half_bin_width )
            left.append(    half_bin_width )
            right.append(   half_bin_width )

        Ts.append( ROOT.TGraphAsymmErrors(
            n_bins,
            array( 'd', centers ),
            array( 'd', mus ),
            array( 'd', left ),
            array( 'd', right ),
            array( 'd', down ),
            array( 'd', up ),
            ))
        Ts[-1].SetName(name)
        Ts[-1].SetLineColor(color)
        Ts[-1].SetMarkerColor(color)
        Ts[-1].Draw('PSAME')


    proposed_bins = bins_WW


    # Some information text boxes
    tl = ROOT.TLatex()
    tl.SetTextSize(0.040)
    tl.SetTextAlign(22)

    lines = []
    for i_bin in range( 1, len(proposed_bins)-1 ):
        lines.append( Line( proposed_bins[i_bin], y_min, proposed_bins[i_bin], y_max ) )
        lines[-1].Draw('LSAME')

        tl.DrawLatex( proposed_bins[i_bin], y_min + (y_max-y_min)*0.9, str(int(proposed_bins[i_bin])) )

    # one_line = Line( 0.0, 1.0, pt_bins[-1], 1.0 )
    # one_line.SetLineStyle(1)
    # one_line.SetLineWidth(2)
    # one_line.Draw('LSAME')

    leg = ROOT.TLegend( 0.78, 0.12, 0.9, 0.3 )
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)

    leg.AddEntry( "gg", "#gamma#gamma", "l")
    leg.AddEntry( "WW", "WW", "l")
    leg.AddEntry( "ZZ", "ZZ", "l")
    leg.Draw()


    c1.Print( 'mu_plot.pdf', '.pdf' )


def Line( x1, y1, x2, y2 ):
    line = ROOT.TLine( x1, y1, x2, y2 )
    line.SetLineStyle(2)
    line.SetLineColor(15)
    line.SetLineWidth(1)
    return line





########################################
# End of Main
########################################
if __name__ == "__main__":
    main()