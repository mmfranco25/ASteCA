"""
@author: gabriel
"""

import matplotlib.pyplot as plt
from functions.display_errors import disp_errors as d_e
from functions.err_accpt_rejct_lowexp import err_a_r_lowexp as e_a_r_le
from functions.err_accpt_rejct_eyefit import err_a_r_eyefit as e_a_r_ef
from functions.err_accpt_rejct_max import err_a_r_m as e_a_r_m


def err_sel_stars(acpt_indx, rjct_indx, phot_data):
    '''
    Go through the lists of indexes to select accepted/rejected stars.
    '''
    # unpack data.
    id_star, x_data, y_data, mag, e_mag, col1, e_col1 = phot_data
    # Initialize empty lists.
    acpt_stars, rjct_stars = [], []

    for st_ind in acpt_indx:
        acpt_stars.append([id_star[st_ind], x_data[st_ind], y_data[st_ind],
            mag[st_ind], e_mag[st_ind], col1[st_ind], e_col1[st_ind]])

    for st_ind in rjct_indx:
        rjct_stars.append([id_star[st_ind], x_data[st_ind], y_data[st_ind],
            mag[st_ind], e_mag[st_ind], col1[st_ind], e_col1[st_ind]])

    return acpt_stars, rjct_stars


def err_accpt_rejct(phot_data, axes_params, er_params, mode, semi_return):
    """
    Accept and reject stars in and out of the cluster's boundaries according to
    a given criteria based on their photometric errors.
    """

    # Unpack data.
    mag, e_mag, e_col1 = phot_data[3], phot_data[4], phot_data[6]
    er_mode, e_max, be = er_params[:3]

    # Get value of brightest and dimmest stars.
    min_mag, max_mag = min(mag), max(mag)
    # Define max limit for the box that holds the brightest stars.
    bright_end = (min_mag + be)
    # Create a segmented list in magnitude.
    # Magnitude range.
    delta_mag = max_mag - bright_end
    # Width of the intervals in magnitude.
    interv_mag = 0.5
    # Number of intervals.
    n_interv = int(delta_mag / interv_mag)
    # Define list of points spanning the magnitude range starting from the
    # bright end.
    mag_value = [bright_end + interv_mag * (q + 0.5) for q in
    range(n_interv - 1)]

    # Pack params to pass.
    err_pck = [er_params, bright_end, n_interv, interv_mag, mag_value]

    # Flag indicates that the function had to fall back to the
    # 'e_max'-based rejection method since the selected one failed.
    err_max_fallback = False
    # Flag indicates that no error rejection was possible.
    err_all_fallback = False

    # Check selected mode.
    if mode in ('auto', 'semi'):
        # If 'semi' is set, check for the flag that indicates which method to
        # use and override the one in the input params file.
        if mode == 'semi':
            # Unpack semi flag
            err_flag_semi = semi_return[4]
            if err_flag_semi != 0:
                if err_flag_semi in {1, 2, 3}:
                    # Set error mode to use.
                    mode_map = {1: 'emax', 2: 'lowexp', 3: 'eyefit'}
                    er_mode = mode_map[int(err_flag_semi)]
                    er_params[0] = er_mode
                    print 'Semi: using method selected: %s.' % er_mode
                else:
                    print ('  WARNING: wrong error method in semi input file.\n'
                    '  Falling back to emax.')
                    er_mode, er_params[0] = 'emax', 'emax'

        # Check which error rejection algorithm was selected in the input
        # file.
        if er_mode == 'emax':
            # Call function to reject stars with errors > e_max.
            acpt_indx, rjct_indx, err_plot = e_a_r_m(e_mag, e_col1, err_pck)

        elif er_mode in ('lowexp', 'eyefit'):
            try:
                if er_mode == 'lowexp':
                    # Call N sigma exp function.
                    acpt_indx, rjct_indx, err_plot = e_a_r_le(mag, e_mag,
                        e_col1, err_pck)

                elif er_mode == 'eyefit':
                    # Call 'eyefit' function.
                    acpt_indx, rjct_indx, err_plot = e_a_r_ef(mag, e_mag,
                        e_col1, err_pck)
            except RuntimeError:
                print ('  WARNING: function could not be fitted. Falling back\n'
                '  to e_max function.')
                # Call function to reject stars with errors > e_max.
                acpt_indx, rjct_indx, err_plot = e_a_r_m(e_mag, e_col1, err_pck)
                err_max_fallback = True

        # If list of accepted stars is empty, fall back to e_max limit.
        if not acpt_indx and er_mode != 'emax':
            # Call function to reject stars with errors > e_max.
            acpt_indx, rjct_indx, err_plot = e_a_r_m(e_mag, e_col1, err_pck)
            err_max_fallback = True

            if acpt_indx:
                print '  WARNING: No stars accepted based on their errors.'
                print '  Using all stars with errors < %0.2f.' % e_max

            # If there's still no accepted stars, use all.
            else:
                print '  WARNING: No stars accepted based on their errors.'
                print '  Using all stars.'
                # Store all indexes.
                acpt_indx, rjct_indx = [i for i in range(len(mag))], []
                err_all_fallback = True

        # If the method used was e_max, use all stars.
        elif not acpt_indx and er_mode == 'emax':
            print '  WARNING: No stars accepted based on their errors.'
            print '  Using all stars.'
            # Store all indexes.
            acpt_indx, rjct_indx = [i for i in range(len(mag))], []
            err_plot = []
            err_all_fallback = True

        # Call function to store stars according to the returned indexes.
        acpt_stars, rjct_stars = err_sel_stars(acpt_indx, rjct_indx, phot_data)

    # If 'manual' mode is set, display errors distributions and ask the user
    # to accept it or else use all stars except those with errors > e_max in
    # either the magnitude or the color.
    elif mode == 'manual':
        move_on = False
        while not move_on:

            wrong_answer = True
            while wrong_answer:
                answer_rad = int(raw_input('Choose a method for error-based '
                'stars rejection:\n  1 (emax), 2 (lowexp), 3 (eyefit), 4 (use '
                'all stars): '))

                if answer_rad == 1:
                    e_max = float(raw_input('Select maximum error value: '))
                    err_pck[0][1] = e_max
                    # Call function to reject stars with errors > e_max.
                    acpt_indx, rjct_indx, err_plot = e_a_r_m(e_mag, e_col1,
                        err_pck)
                    wrong_answer = False
                    er_mode, er_params[0] = 'emax', 'emax'
                elif answer_rad == 2:
                    N_sig = float(raw_input("Select number of sigmas to lift"
                    " the curve: "))
                    err_pck[0][-1] = N_sig
                    # Call N sigma exp function.
                    acpt_indx, rjct_indx, err_plot = e_a_r_le(mag, e_mag,
                        e_col1, err_pck)
                    wrong_answer = False
                    er_mode, er_params[0] = 'lowexp', 'lowexp'
                elif answer_rad == 3:
                    # Call 'eyefit' function.
                    acpt_indx, rjct_indx, err_plot = e_a_r_ef(mag, e_mag,
                        e_col1, err_pck)
                    wrong_answer = False
                    er_mode, er_params[0] = 'eyefit', 'eyefit'
                elif answer_rad == 4:
                    # Store all indexes.
                    acpt_indx, rjct_indx = [i for i in range(len(mag))], []
                    err_plot, er_params[0] = [], ''
                    err_all_fallback = True
                    wrong_answer = False

                if answer_rad not in {1, 2, 3, 4}:
                    print 'Wrong input. Try again.\n'
                else:
                    if len(acpt_indx) == 0:
                        print  ('No stars left after error rejection. Try'
                        ' again with a different method or use all stars (4).')
                    else:
                        wrong_answer = False

            # Call function to store stars according to the returned indexes.
            acpt_stars, rjct_stars = err_sel_stars(acpt_indx, rjct_indx,
                phot_data)

            if answer_rad != 4:
                print 'Plot error distributions.'
                # Display automatic errors rejection.
                d_e(er_mode, mag, err_plot, acpt_stars, rjct_stars, err_pck,
                    axes_params)
                plt.show()
                # Ask if keep or reject.
                wrong_answer = True
                while wrong_answer:
                    mv_on = str(raw_input('Accept fit for errors? (y/n) '))
                    if mv_on == 'y':
                        print 'Fit accepted.'
                        wrong_answer = False
                        move_on = True
                    elif mv_on == 'n':
                        wrong_answer = False
            else:
                move_on = True

    print 'Stars accepted/rejected based on their errors.'

    err_flags = [err_all_fallback, err_max_fallback]
    return acpt_stars, rjct_stars, err_plot, err_flags, err_pck, er_params