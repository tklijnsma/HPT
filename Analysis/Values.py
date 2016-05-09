
########################################
# Main
########################################

def main():

    ########################################
    # All the input
    ########################################

    pt_bins = [ 0, 15, 26, 43, 72, 125, 200, 300 ]

    # Values from paper
    gg_XS          = [ 9.0, 2.0, 3.4, 6.2, 4.6, 2.6, 0.7 ],
    gg_XS_err_up   = [ 6.4, 4.9, 4.8, 3.7, 2.4, 1.0, 0.5 ],
    gg_XS_err_down = [ -6.2, -5.5, -4.6, -3.5, -2.7, -1.0, -0.4 ],

    # Total number of generated events ~ 53k
    kt1_entries = [ 8226.0, 7124.0, 6958.0, 5648.0, 3314.0, 1105.0, 432.0 ]
    kg1_entries = [ 8871.0, 7302.0, 6853.0, 5286.0, 3000.0, 1002.0, 489.0 ]

    betas_over_alpha = [ 0.962959590786, 0.987736360045, 1.00763175659, 1.03367440943, 1.05103123962, 1.05014018644, 0.939912539986, ]


    ########################################
    # Some tests when given a specific kt and kg
    ########################################

    print '\nActual number of entries for kt = 1.0, kg = 0.0'
    print [ '{:.2f}'.format(i) for i in kt1_entries ]

    print '\nExpected number of entries for kt = 1.0, kg = 0.0'
    Exp_number_of_entries(
        # Given kt
        1.0,
        # Given kg
        0.0,
        # Necessary input
        kt1_entries,
        kg1_entries,
        betas_over_alpha,
        )


    print '\nActual number of entries for kt = 0.0, kg = 1.0'
    print [ '{:.2f}'.format(i) for i in kg1_entries ]

    print '\nExpected number of entries for kt = 0.0, kg = 1.0'
    Exp_number_of_entries(
        # Given kt
        0.0,
        # Given kg
        1.0,
        # Necessary input
        kt1_entries,
        kg1_entries,
        betas_over_alpha,
        )



    print '\nExpected number of entries for kt = 0.5, kg = 0.5'
    Exp_number_of_entries(
        # Given kt
        0.5,
        # Given kg
        0.5,
        # Necessary input
        kt1_entries,
        kg1_entries,
        betas_over_alpha,
        )


    print '\nExpected number of entries for kt = 0.3, kg = 0.7'
    Exp_number_of_entries(
        # Given kt
        0.3,
        # Given kg
        0.7,
        # Necessary input
        kt1_entries,
        kg1_entries,
        betas_over_alpha,
        )


########################################
# Functions
########################################

def Exp_number_of_entries(

        # Given kt1 and kg1
        kt, kg,

        # Necessary input
        kt1_entries,
        kg1_entries,
        betas_over_alpha,

        ):

    n_bins = len(kt1_entries)

    exp_events = []
    for i in range(n_bins):

        exp_events.append(
            ( kg + betas_over_alpha[i] * kt )**2 * kg1_entries[i]
            )

    print [ '{:.2f}'.format(i) for i in exp_events ]



########################################
# End of Main
########################################
if __name__ == "__main__":
    main()