from Spectrum import Spectra_container

from array import array
from math import pi, sqrt, exp, log

import os
import numpy

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = kError;")
ROOT.RooMsgService.instance().setSilentMode(True)


def kappa_plot( self, plot_appendix='', luminosity='default', diagonal_corr=False ):
    n_points = len(self.data.values)
    n_bins   = n_points

    if luminosity == 'default':
        luminosity = self.default_luminosity


    # Read cross sections into lists
    s_data          = self.data.values[:]
    s_data_err_up   = self.data.err_up[:]
    s_data_err_down = self.data.err_down[:]
    s_data_err_symm = [ 0.5*(abs(i)+abs(j)) for i, j in zip( s_data_err_up, s_data_err_down ) ]

    s_kt1 = self.kt1.values[:]
    s_kg1 = self.kg1.values[:]


    ########################################
    # Open a canvas and draw a base
    ########################################

    if not hasattr( self, 'c' ):
        self.c = ROOT.TCanvas( 'c', 'c', 1000, 700 )
    else:
        self.c.Clear()
        self.c.SetLogy(False)
        self.c.SetGrid(False)


    BottomMargin = 0.12
    LeftMargin   = 0.10
    TopMargin    = 0.06
    RightMargin  = 0.14

    self.c.SetBottomMargin( BottomMargin )
    self.c.SetLeftMargin(   LeftMargin )
    self.c.SetTopMargin(    TopMargin )
    self.c.SetRightMargin(  RightMargin )

    y_marg = 1.0 - RightMargin - LeftMargin
    x_marg = 1.0 - TopMargin - BottomMargin

    h = 700
    w = int(h / y_marg * x_marg)

    self.c.SetCanvasSize( w, h )


    x_min = 0.0
    x_max = 2.0
    y_min = 0.0
    y_max = 2.0

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

    # base.GetZaxis().SetRangeUser( 0., 1. )

    base.Draw('P')


    ########################################
    # This is RooFit
    ########################################

    # ======================================
    # Get inverse covariance matrix


    if diagonal_corr:
        # OLD WAY, simple diagonal matrix
        
        # Creates an array of length N filled with zeroes, except at index i_nonzero (then it's 1)
        zero_array = lambda N, i_nonzero, val: [ 0. if i!=i_nonzero else val for i in xrange(N)]
        
        C = []
        for i_bin in xrange(n_bins):
            C.append( zero_array( n_bins, i_bin, s_data_err_symm[i_bin]**2 ) )
        C = numpy.array(C)

    else:
        # Give an actual matrix
        # NOTE: THIS IS OFF DIAGONAL NOW!!
        corr = numpy.transpose( numpy.array([
            [ 0.01,    -0.01,   0.04,    0.04,    -0.03,   0.05,    1.00,   ],
            [ -0.05,   0.03,    -0.04,   0.03,    0.01,    1.00,    0.05,   ],
            [ 0.00,    -0.07,   0.05,    0.00,    1.00,    0.01,    -0.03,  ],
            [ 0.04,    0.00,    -0.04,   1.00,    0.00,    0.03,    0.04,   ],
            [ 0.07,    -0.12,   1.00,    -0.04,   0.05,    -0.04,   0.04,   ],
            [ -0.11,   1.00,    -0.12,   0.00,    -0.07,   0.03,    -0.01,  ],
            [ 1.00,    -0.11,   0.07,    0.04,    0.00,    -0.05,   0.01,   ],
            ] ))

        C = numpy.array( [ [ 0. for j in xrange(n_bins) ] for i in xrange(n_bins) ] )

        for i in xrange(n_bins):
            for j in xrange(n_bins):
                C[i][j] = corr[i][j] * s_data_err_symm[i] * s_data_err_symm[j]


    # Take inverse
    C_inv = numpy.linalg.inv(C)

    # print '\nCovariance matrix:'
    # print C

    # print '\nInverse covariance matrix:'
    # print C_inv
    # print


    # ======================================
    # Get the chi2 RooFormulaVar

    # Open up the vars to scan with
    kt = ROOT.RooRealVar( 'kt', 'kt', 1., 0., 3. )
    kg = ROOT.RooRealVar( 'kg', 'kg', 1., 0., 3. )

    chi2 = self.Get_chi2_formula( kt, kg, C_inv, plot_appendix )



    ########################################
    # Minimization for maximum likelihood
    ########################################

    print '\n' + '='*70
    print 'Initializing Minimizer'
    print

    Minimizer = ROOT.RooMinimizer( chi2 )

    print '\nSuccesfully initialized the Minimizer, now trying MIGRAD'
    print

    Minimizer.migrad()
    Minimizer.minos()


    # Read of the minimum function value
    self.chi2_minimum = chi2.getVal()
    self.kt_minimum = kt.getVal()
    self.kg_minimum = kg.getVal()

    # Calculate the spectrum that fits data best
    self.best_fit = []
    for i_bin in xrange(n_bins):
        xs = self.kg_minimum**2 * s_kg1[i_bin]  +  self.kt_minimum**2 * s_kt1[i_bin]
        if self.OC_filled: xs += self.OC_XS[i_bin]
        self.best_fit.append( xs )


    ########################################
    # Scan
    ########################################

    scan = Minimizer.contour( kg, kt, 1, 0 )

    scan.Print()


    # color = 2
    # scan.getObject(0).SetMarkerColor(color)
    # scan.getObject(1).SetLineColor(color)

    # Draw later
    # scan.Draw('SAME')



    ########################################
    # Manual scan
    ########################################

    nx = 200
    ny = 200
    H2 = ROOT.TH2F(
        'H2', '',
        nx, x_min, x_max,
        ny, y_min, y_max
        )

    for i_binx in xrange(nx):
        for i_biny in xrange(ny):

            x_bincenter = H2.GetXaxis().GetBinCenter(i_binx+1)
            y_bincenter = H2.GetXaxis().GetBinCenter(i_biny+1)
    
            kg.setVal( x_bincenter )
            kt.setVal( y_bincenter )

            H2.SetBinContent(
                i_binx+1, i_biny+1,
                chi2.getVal() - self.chi2_minimum
                )


    # Define color scheme
    ROOT.TColor.CreateGradientColorTable(
        7,
        array('d', [ 0.00, 0.05, 0.23, 0.35, 0.58, 0.88, 1.00 ] ),
        array('d', [ 1.00, 1.00, 0.00, 0.40, 0.87, 1.00, 0.85 ] ),
        array('d', [ 1.00, 1.00, 0.71, 0.81, 1.00, 0.20, 0.00 ] ),
        array('d', [ 1.00, 1.00, 1.00, 1.00, 0.18, 0.00, 0.00 ] ),
        103 )


    H2.GetZaxis().SetRangeUser( 0., 4. )



    # scan.Draw('SAME')

    H2.Draw('SAME COLZ')


    lumi_label = ROOT.TLatex()
    lumi_label.SetNDC()
    lumi_label.SetTextSize(0.045)
    lumi_label.SetTextAlign(31)
    lumi_label.DrawLatex( 1.0-RightMargin+0.005, 1.0-TopMargin+0.005, 'L = {0:.1f} fb^{{-1}}'.format(luminosity) )

    outfilename = 'kgktPlane' + plot_appendix + '.pdf'
    self.c.SaveAs( os.path.join( self.plotdir, outfilename ) )





    ########################################
    # Reparametrize into phi and r (radial coordinates in kg-kt plane)
    ########################################


    print '\n' + '='*70
    print 'Reparametrizing to radial coordinates\n'


    phi = ROOT.RooRealVar( 'phi', 'phi', 0. )
    phi.setConstant()

    r =   ROOT.RooRealVar( 'r', 'r',     1., 0., 10. )


    # Change the definitions of kt and kg (also in RooFit)
    kt = ROOT.RooFormulaVar(
        'kt', 'kt',
        'r*sin(phi)',
        ROOT.RooArgList(r,phi)
        )

    kg = ROOT.RooFormulaVar(
        'kg', 'kg',
        'r*cos(phi)',
        ROOT.RooArgList(r,phi)
        )


    chi2 = self.Get_chi2_formula( kt, kg, C_inv, plot_appendix )
    Minimizer = ROOT.RooMinimizer( chi2 )

    n_phi_points = 100
    phi_min = 0.0
    phi_max = 0.5*pi
    phi_axis = [ phi_min + (phi_max-phi_min)/(n_phi_points-1)*i for i in xrange(n_phi_points) ]


    chi2_axis = []
    for phi_value in phi_axis:

        phi.setVal( phi_value )

        Minimizer.migrad()
        Minimizer.minos()

        # Read off the minimum function value (take offset into account so that 0.0 is the lowest possible chi2)
        chi2_axis.append( chi2.getVal() - self.chi2_minimum )


    # Clear canvas
    self.c.Clear()
    self.c.SetGrid()

    BottomMargin = 0.12
    LeftMargin   = 0.15
    TopMargin    = 0.06
    RightMargin  = 0.03

    self.c.SetBottomMargin( BottomMargin )
    self.c.SetLeftMargin(   LeftMargin )
    self.c.SetTopMargin(    TopMargin )
    self.c.SetRightMargin(  RightMargin )

    y_marg = 1.0 - RightMargin - LeftMargin
    x_marg = 1.0 - TopMargin - BottomMargin

    h = 700
    w = int(h / y_marg * x_marg)

    self.c.SetCanvasSize( w, h )



    x_min = phi_min
    x_max = phi_max
    y_min = min( 0.0, min(chi2_axis) )
    y_max = 1.1 * max(chi2_axis)

    base.SetMinimum( y_min )
    base.SetMaximum( y_max )
    base.GetXaxis().SetLimits( x_min, x_max )
    base.GetXaxis().SetTitle('#phi')
    base.GetXaxis().SetTitleOffset(0.7)
    base.GetYaxis().SetTitle('#chi^{2}')
    base.GetYaxis().SetTitleOffset(1.1)
    base.Draw('P')


    TG_phi = ROOT.TGraph( n_phi_points, array( 'd', phi_axis ), array( 'd', chi2_axis ) )
    TG_phi.SetLineWidth(2)
    TG_phi.Draw('SAMEL')

    lumi_label = ROOT.TLatex()
    lumi_label.SetNDC()
    lumi_label.SetTextSize(0.045)
    lumi_label.SetTextAlign(31)
    lumi_label.DrawLatex( 1.0-RightMargin+0.005, 1.0-TopMargin+0.005, 'L = {0:.1f} fb^{{-1}}'.format(luminosity) )


    outfilename = 'PhiScan' + plot_appendix + '.pdf'
    self.c.SaveAs( os.path.join( self.plotdir, outfilename ) )




def Get_chi2_formula( self, kt, kg, C_inv, plot_appendix='', verbose=False ):
    n_points = len(self.data.values)
    n_bins   = n_points

    s_data          = self.data.values[:]
    s_data_err_up   = self.data.err_up[:]
    s_data_err_down = self.data.err_down[:]
    s_data_err_symm = [ 0.5*(abs(i)+abs(j)) for i, j in zip( s_data_err_up, s_data_err_down ) ]


    s_kt1 = self.kt1.values[:]
    s_kg1 = self.kg1.values[:]


    # Open list for object persistence
    if not hasattr( self, 'Persistence' ): self.Persistence = []


    if verbose: print '\nFilling RooFormulaVars for bins'

    # Make a RooFormulaVar per bin, that takes k_t and k_g
    Sigmas = []
    for i_bin in xrange(n_bins):

        # beta_over_alpha = sqrt(  s_kt1[i_bin] / s_kg1[i_bin]  )

        if verbose:
            printstring = 'Bin {0}  |  XS for k_g==1: {1:7.4f}  |   XS for k_t==1: {2:7.4f}'.format(
                i_bin,
                s_kg1[i_bin],
                s_kt1[i_bin],
                )
            if self.OC_filled:
              printstring += '|  XS contr from OC: {0:7.4f}'.format( self.OC_XS[i_bin] )
            print printstring


        binname = 'bin' + str(i_bin)

        if self.OC_filled:
            # This assumes the contributions from other channels are known
            Sigma = ROOT.RooFormulaVar(
                binname, binname,
                '{0} * kg**2  +  {1} * kt**2  -  {2}  +  {3}'.format( s_kg1[i_bin], s_kt1[i_bin], s_data[i_bin], self.OC_XS[i_bin] ),
                ROOT.RooArgList( kt, kg )
                )
        else:
            # This only if other channel contributions are not available
            Sigma = ROOT.RooFormulaVar(
                binname, binname,
                '{0} * kg**2  +  {1} * kt**2  -  {2}'.format( s_kg1[i_bin], s_kt1[i_bin], s_data[i_bin] ),
                ROOT.RooArgList( kt, kg )
                )

        Sigmas.append( Sigma )
        self.Persistence.append( Sigma )


    separate_products = ROOT.RooArgList()
    
    for i in xrange(n_bins):
        for j in xrange(n_bins):

            if C_inv[i][j] == 0.: continue

            C_ij = ROOT.RooFit.RooConst( C_inv[i][j] )

            productname = 'product{0}{1}'.format(i,j)
            product = ROOT.RooProduct( productname, productname,  ROOT.RooArgList( Sigmas[i], C_ij, Sigmas[j] )   )

            separate_products.add( product )

            self.Persistence.append( C_ij )
            self.Persistence.append( product )


    chi2 = ROOT.RooAddition( 'chi2', 'chi2', separate_products )
    
    # print "This is chi2.Print('v'):"
    # chi2.Print('v')

    # print '\nTest evaluation of chi2:'
    # for kg_test, kt_test in [ (0,0), (0,1), (1,0), (1,1) ]:
    #     kg.setVal( kg_test )
    #     kt.setVal( kt_test )
    #     print '  kg = {0:.1f}  |  kt = {1:.1f}  |  chi2 = {2}'.format( kg_test, kt_test, chi2.getVal() )

    return chi2





Spectra_container.kappa_plot = kappa_plot
Spectra_container.Get_chi2_formula = Get_chi2_formula