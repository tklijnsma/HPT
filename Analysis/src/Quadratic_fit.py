from Spectrum import Spectrum
from Spectrum import Spectra_container

import ROOT
import os
from math import sqrt

from array import array


def Quadratic_fit( spec ):

    # Convenience pointers
    kt1 = spec.kt1.H
    kg1 = spec.kg1.H


    # Define:
    #  sigma  =  | alpha * kappa_t  +  beta * kappa_g |^2

    # then
    #  alpha / beta  =  sqrt( sigma_i / sigma_j )
    #  beta / alpha  =  sqrt( sigma_j / sigma_i )

    spec.ratios = []

    for i in range(spec.n_pt_bins):

        alpha_over_beta = sqrt(spec.kt1.unnormalized_values[i] / spec.kg1.unnormalized_values[i])
        beta_over_alpha = sqrt(spec.kg1.unnormalized_values[i] / spec.kt1.unnormalized_values[i])

        spec.ratios.append( beta_over_alpha )


    print 'Ratios sigma_{kg-sample} over sigma_{kt-sample}:'

    for i in range(spec.n_pt_bins):

        print '    bin {0:2} | pt: {1:<4} to {2:<4} GeV | beta over alpha: {3}'.format(
            i,
            int(spec.pt_bins[i]),
            int(spec.pt_bins[i+1]),
            spec.ratios[i]
            )

