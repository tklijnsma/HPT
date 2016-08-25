from Spectrum import Spectra_container

from array import array
from math import pi, sqrt, exp, log
import numpy

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kError;")
# ROOT.RooMsgService.instance().setSilentMode(True)


def kappa_plot( self ):

    n_points = len(self.data.values)
    n_bins   = n_points

    # Normalized cross section
    s_data = [ s/sum(self.data.values) for s in self.data.values ]
    s_kt1  = [ s/sum(self.kt1.values) for s in self.kt1.values ]
    s_kg1  = [ s/sum(self.kg1.values) for s in self.kg1.values ]

    s_data_err_up   = [ s/sum(self.data.err_up) for s in self.data.err_up ]
    s_data_err_down = [ s/sum(self.data.err_down) for s in self.data.err_down ]
    s_data_err_symm = [ 0.5*(abs(i)+abs(j)) for i, j in zip( s_data_err_up, s_data_err_down ) ]


    # print s_data
    # print s_kt1
    # print s_kg1

    kappa = lambda s, s_SM: sqrt( s / s_SM )
    kappa_err = lambda s, s_err, s_SM: abs( kappa( max(s+s_err,0.), s_SM ) - kappa( s, s_SM ) )

    kt_center    = [ sqrt( s / s_SM ) for s, s_SM in zip( s_data, s_kt1 ) ]
    kt_err_up    = [ kappa_err( s, s_err, s_SM ) for s, s_err, s_SM in zip( s_data, s_data_err_up, s_kt1 ) ]
    kt_err_down  = [ kappa_err( s, -abs(s_err), s_SM ) for s, s_err, s_SM in zip( s_data, s_data_err_down, s_kt1 ) ]
    kt_err_symm  = [ 0.5*(abs(up)+abs(down))  for up, down in zip(kt_err_up,kt_err_down) ]

    kg_center    = [ sqrt( s / s_SM ) for s, s_SM in zip( s_data, s_kg1 ) ]
    kg_err_up    = [ kappa_err( s, s_err, s_SM ) for s, s_err, s_SM in zip( s_data, s_data_err_up, s_kg1 ) ]
    kg_err_down  = [ kappa_err( s, -abs(s_err), s_SM ) for s, s_err, s_SM in zip( s_data, s_data_err_down, s_kg1 ) ]
    kg_err_symm  = [ 0.5*(abs(up)+abs(down))  for up, down in zip(kg_err_up,kg_err_down) ]



    if not hasattr( self, 'c' ): self.c = ROOT.TCanvas( 'c', 'c', 1000, 700 )

    self.c.SetBottomMargin( 0.12 )
    self.c.SetLeftMargin(   0.10 )
    self.c.SetTopMargin(    0.04 )
    self.c.SetRightMargin(  0.14 )

    x_min = 0.0
    x_max = 1.0
    y_min = 0.0
    y_max = 1.0

    x_min = -0.5
    x_max = 2.5
    y_min = -0.5
    y_max = 2.5

    # base owns the axes
    base = ROOT.TH1F()
    base.SetTitle('')

    base.SetMinimum( y_min )
    base.SetMaximum( y_max )
    base.GetXaxis().SetLimits( x_min, x_max )

    base.GetXaxis().SetTitle('#kappa_{g}')
    base.GetXaxis().SetTitleSize(0.065)
    base.GetXaxis().SetTitleOffset(0.86)
    base.GetXaxis().SetLabelSize(0.05)
    # base.GetXaxis().SetNdivisions(505)
    
    base.GetYaxis().SetTitle('#kappa_{t}')
    base.GetYaxis().SetTitleSize(0.065)
    base.GetYaxis().SetTitleOffset(0.75)
    base.GetYaxis().SetLabelSize(0.05)
    # base.GetYaxis().SetNdivisions(505)

    base.Draw('P')



    ########################################
    # Fill 2D histo
    ########################################


    # THIS IS PYTHON STYLE

    # Gauss = lambda x, mu, sigma: 1./( sqrt(2*pi)*sigma )  *  exp(-0.5*(  (x-mu)/sigma  )**2)

    # def TH2_function( kg, kt ):

    #     res = 1.0

    #     for i_point in xrange(n_points):

    #         res *= (
    #             Gauss( kg, kg_center[i_point], kg_err_symm[i_point] )
    #             *
    #             Gauss( kt, kt_center[i_point], kt_err_symm[i_point] )
    #             )
    #     return res


    # # The 2D histogram to loop integration over
    # nx = 100
    # ny = 100
    # H2 = ROOT.TH2F(
    #     'H2', '',
    #     nx, x_min, x_max,
    #     ny, y_min, y_max
    #     )

    # for i_binx in xrange(nx):
    #     for i_biny in xrange(ny):

    #         x_bincenter = H2.GetXaxis().GetBinCenter(i_binx+1)
    #         y_bincenter = H2.GetXaxis().GetBinCenter(i_biny+1)
    
    #         H2.SetBinContent(
    #             i_binx+1, i_biny+1,
    #             TH2_function( x_bincenter, y_bincenter )
    #             )


    # # Define color scheme
    # ROOT.TColor.CreateGradientColorTable(
    #     7,
    #     array('d', [ 0.00, 0.05, 0.25, 0.36, 0.58, 0.88, 1.00 ] ),
    #     array('d', [ 1.00, 1.00, 0.00, 0.40, 0.87, 1.00, 0.85 ] ),
    #     array('d', [ 1.00, 1.00, 0.71, 0.81, 1.00, 0.20, 0.00 ] ),
    #     array('d', [ 1.00, 1.00, 1.00, 1.00, 0.18, 0.00, 0.00 ] ),
    #     103 )


    # H2.Draw('SAME COLZ')





    # This is RooFit style


    # Make covariance matrix (have to change at some point)
    zero_array = lambda N, i_nonzero, val: [ 0. if i!=i_nonzero else val for i in xrange(N)]
    C = []
    for i_bin in xrange(n_bins):
        C.append( zero_array( n_bins, i_bin, s_data_err_symm[i_bin] ) )
    C = numpy.array(C)
    print C

    # ACTUAL covariance matrix
    # [ 0.01,    -0.01,   0.04,    0.04,    -0.03,   0.05,    1.00,   ]
    # [ -0.05,   0.03,    -0.04,   0.03,    0.01,    1.00,    0.05,   ]
    # [ 0.00,    -0.07,   0.05,    0.00,    1.00,    0.01,    -0.03,  ]
    # [ 0.04,    0.00,    -0.04,   1.00,    0.00,    0.03,    0.04,   ]
    # [ 0.07,    -0.12,   1.00,    -0.04,   0.05,    -0.04,   0.04,   ]
    # [ -0.11,   1.00,    -0.12,   0.00,    -0.07,   0.03,    -0.01,  ]
    # [ 1.00,    -0.11,   0.07,    0.04,    0.00,    -0.05,   0.01,   ]



    # Take inverse
    C_inv = numpy.linalg.inv(C)
    print C_inv

    # RooCs = []
    # for i_bin in xrange(n_bins):
    #     for j_bin in xrange(n_bins):





    # Open up the vars to scan with
    kt = ROOT.RooRealVar( 'kt', 'kt', 0., -10., 10. )
    kg = ROOT.RooRealVar( 'kg', 'kg', 0., -10., 10. )


    # Make a RooFormulaVar per bin, that takes k_t and k_g
    binFormVars = []
    for i_bin in xrange(n_bins):

        beta_over_alpha = self.ratios[i_bin]

        binname = 'bin' + str(i_bin)

        binFormVar = ROOT.RooFormulaVar(
            binname, binname,
            '(kg + {0}*kt)**2 * {1} - {2}'.format( beta_over_alpha, s_kt1[i_bin], s_data[i_bin] )
            )

        binFormVars.append( binFormVar )


    # TODO:
    # First matrix multiplication --> Gives n_bins RooFormulaVars
    # Make all the sums --> v1(i) * v2(j), gives n_bins**2 RooProducts
    # Make chi2 = RooAddition of the 25 RooProducts



    chi2_formula = '-2.0*(0.'
    chi2_counter = 0
    chi2_arglist = ROOT.RooArgList()


    # for i_bin in xrange(n_bins):

    #     chi2_formula += 












    # Actual data points


    Tk = ROOT.TGraphAsymmErrors(
        len(s_data),
        array( 'd', kg_center ),
        array( 'd', kt_center ),
        array( 'd', kg_err_down ),
        array( 'd', kg_err_up ),
        array( 'd', kt_err_down ),
        array( 'd', kt_err_up ),
        )

    Tk.SetMarkerStyle(8)
    Tk.Draw('SAME P')







    self.c.SaveAs( 'kappa1.pdf' )






















Spectra_container.kappa_plot = kappa_plot

