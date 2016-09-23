import sys
sys.path.append('src')


import ROOT
import argparse
import os

from array import array
from copy import deepcopy


########################################
# Main
########################################

ROOT.gROOT.SetBatch(True)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kError;")

c = ROOT.TCanvas( 'c1', 'c1', 800, 600 )
plotdir = 'plots_Quantiles'


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument( '--redraw', action='store_true', help='Forces the program to redraw the histograms from the root files')
    args = parser.parse_args()


    # ../Apply_flashgg/Saved_root_files/20Sep/flashgg_0812_kg1_gg_H.root
    # ../Apply_flashgg/Saved_root_files/20Sep/flashgg_0812_kt1_gg_H_quark-mass-effects.root


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
        # 'pt > 100'

        ]


    # ======================================
    # Get histos (and make quick plots for them)

    H_kg = GetTH2( 'kg', '../Apply_flashgg/Saved_root_files/20Sep/flashgg_0812_kg1_gg_H.root', cuts )
    H_kt = GetTH2( 'kt', '../Apply_flashgg/Saved_root_files/20Sep/flashgg_0812_kt1_gg_H_quark-mass-effects.root', cuts )


    # ======================================
    # Plot the profiles

    PX_kg = H_kg.ProfileX()
    PX_kg.SetLineColor(2)

    PX_kt = H_kt.ProfileX()
    PX_kt.SetLineColor(4)

    c.Clear()
    PX_kt.Draw()
    PX_kg.Draw("same")

    SaveCanvas( c, 'Profiles.pdf' )


    # ======================================
    # Quantiles


    quantiles = [ 0., 0.25, 0.5, 0.75 ]
    title = 'Quantiles: ' + ' - '.join([ '{0:.1f}'.format(100*q) for q in quantiles ])

    QTGs_kg = getQuantilesGraphs( H_kg, quantiles, twosided=False )
    QTGs_kt = getQuantilesGraphs( H_kt, quantiles, twosided=False )

    globalMax = 1.2 * max([ ROOT.TMath.MaxElement( TG.GetN(), TG.GetY() ) for TG in QTGs_kg + QTGs_kt ])

    c.Clear()


    kg_color = 2
    kt_color = 4

    for iQuantile in xrange(len(QTGs_kg)):
        kg_QTG = QTGs_kg[iQuantile]
        kt_QTG = QTGs_kt[iQuantile]

        kg_QTG.SetLineColor(kg_color)
        kg_QTG.SetMarkerColor(kg_color)

        kt_QTG.SetLineColor(kt_color)
        kt_QTG.SetMarkerColor(kt_color)

        if iQuantile == 0:
            kg_QTG.SetTitle( title )
            kg_QTG.Draw()
            kg_QTG.SetMaximum(globalMax)

        else:
            kg_QTG.Draw("SAME")
        kt_QTG.Draw("SAME")

    SaveCanvas( c, 'Quantiles.pdf'.format(iQuantile) )











########################################
# Functions
########################################



def getQuantilesGraphs(histo,probs,twosided=False,errors=True,sign=1):
    from math import sqrt
    ## histo.Print("all")
    graphs = [ ]
    if len(probs) == 0:
        return graphs
    for p in probs:
        gr = ROOT.TGraphErrors(histo.GetNbinsX())
        gr.SetName("%s_quantile_%1.2f"%(histo.GetName(),100.*p))
        graphs.append(gr)
    ## graphs = [ ROOT.TGraphErrors(histo.GetNbinsX()) for p in probs ]
    if twosided:
        qtiles = []
        for p in probs:
            t = 0.5 - p*0.5
            qtiles.append( t )
            qtiles.append( 1-t )
    else:
        if sign > 0:
            qtiles=probs
        else:
            qtiles = [1.-p for p in probs]
        
    nq = len(qtiles)
    graph = ROOT.TGraph(nq+2)
    for iq in range(nq):
        graph.SetPoint(iq,qtiles[iq],0.)
    for g in graphs:        
        g.GetXaxis().SetTitle(histo.GetXaxis().GetTitle())
        g.SetMarkerStyle(histo.GetMarkerStyle())
    graph.SetPoint(nq,0.25,0.)
    graph.SetPoint(nq+1,0.75,0.)
        
    for ix in range(1,histo.GetNbinsX()+1):
        proj = histo.ProjectionY("qtiles",ix,ix)
        
        ## proj.Print("all")
        ## graph.Print("all")
        proj.GetQuantiles(nq+2,graph.GetY(),graph.GetX())
        ntot = proj.Integral()
        if ntot == 0: continue
        h = 1.2*( graph.GetY()[nq+1] - graph.GetY()[nq] ) * pow(ntot,-0.2)
        
        if twosided:
            for ig in range(nq/2):                
                quant1 = graph.GetY()[ig]
                quant2 = graph.GetY()[ig+1]
                quant = (quant2 - quant1)*0.5                
                quant1mh = proj.FindBin( quant1 - h*0.5 )
                quant1ph = proj.FindBin( quant1 + h*0.5 )
                quant2mh = proj.FindBin( quant2 - h*0.5 )
                quant2ph = proj.FindBin( quant2 + h*0.5 )
                
                nint = proj.Integral( quant1mh, quant1ph ) + proj.Integral( quant2mh, quant2ph )
                fq = nint / (2.*h*ntot)
                
                graphs[ig/2].SetPoint(ix-1,histo.GetXaxis().GetBinCenter(ix),quant)
                if errors:
                    err = 1./(2.*sqrt(ntot)*fq)
                    graphs[ig/2].SetPointError(ix-1,histo.GetXaxis().GetBinWidth(ix)*0.5,err)
                else:
                    graphs[ig/2].SetPointError(ix-1,histo.GetXaxis().GetBinWidth(ix)*0.5,0.)
                
        else:
            for ig in range(nq):
                quant = graph.GetY()[ig]
                quantmh = proj.FindBin( quant - h )
                quantph = proj.FindBin( quant + h )
                nint = proj.Integral( quantmh, quantph )
                fq = nint / (2.*h*ntot)
                
                graphs[ig].SetPoint(ix-1,histo.GetXaxis().GetBinCenter(ix),quant)
                if errors:
                    err = 1./(2.*sqrt(ntot)*fq)
                    graphs[ig].SetPointError(ix-1,histo.GetXaxis().GetBinWidth(ix)*0.5,err)
                else:
                    graphs[ig].SetPointError(ix-1,histo.GetXaxis().GetBinWidth(ix)*0.5,0.)
                
    return graphs




def GetTH2( name, root_file, cuts ):

    rootFp = ROOT.TFile( root_file )
    rootFp.cd('genDiphotonDumper/trees')
    tree  = ROOT.gDirectory.Get( 'ggH_all' )

    pt_axis = linAxis( 40, 0., 100., ) + linAxis( 20, 100., 200. ) + linAxis( 5, 200., 300. ) + [ 300. ]

    # print pt_axis
    # sys.exit()

    Hname = name; Htitle = name
    H = ROOT.TH2F( Hname, Htitle,
        # 100, 0., 300.,
        len(pt_axis)-1, array( 'd', pt_axis ),
        100, 0., 5.,
        )


    selStr  = parseSelString( cuts )
    drawStr = 'abs(rapidity-jet0Rapidity):pt'

    tree.Draw( drawStr + '>>' + Hname, selStr )

    H.Draw('colz')

    SaveCanvas( c, 'H2D_{0}.pdf'.format(name) )

    return deepcopy(H)


# Linear axis, does NOT reach endpoint e, but is 1 step short of it (easier concatenation)
def linAxis( n, b, e ):
    d = (e-b)/n
    return [ b + i*d for i in xrange(n) ]


def parseSelString( listOfSelectionStrings ):

    # Copy list so it won't change
    sels = listOfSelectionStrings[:]

    # Start with first one
    sel_str = sels.pop(0)

    # Parse the other parts
    for sel in sels:
        sel_str += '&& (' + sel + ')'

    return sel_str



def SaveCanvas( canvas, outname, plotDirectory=plotdir ):
    if not os.path.isdir( plotDirectory ): os.makedirs(plotDirectory)
    canvas.SaveAs( os.path.join( plotDirectory, outname ) )


########################################
# End of Main
########################################
if __name__ == "__main__":
    main()