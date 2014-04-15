# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 2014

@author: gabriel
"""


def red_memb(decont_algor_return, bf_params, rm_params):
    '''
    Reduce number of stars according to a given membership probability
    lower limit.
    '''

    bf_flag = bf_params[0]
    memb_prob_avrg_sort, flag_decont_skip = decont_algor_return
    flag_red_memb, min_prob = rm_params

    # Only run if best fit process is set to run.
    if bf_flag:

        skip_reduce = False
        if flag_red_memb in {'auto', 'manual'}:

            if flag_decont_skip is True:
                print "WARNING: decontamination algorithm skipped."
                print "Can't apply membership reduction."
                skip_reduce = True

            if skip_reduce is not True:

                if flag_red_memb == 'auto':
                    # Reject stars in the lower half of the membership
                    # probabilities list.
                    middle_indx = int(len(memb_prob_avrg_sort) / 2)
                    # Check number of stars left.
                    if len(memb_prob_avrg_sort[:middle_indx]) < 10:
                        print 'WARNING: less than 10 stars left after reducing'
                        print 'by membership prob. Using full list.'
                        red_memb_prob, min_prob = memb_prob_avrg_sort, 0.
                    else:
                        red_memb_prob = memb_prob_avrg_sort[:middle_indx]
                        min_prob = memb_prob_avrg_sort[middle_indx][7]

                elif flag_red_memb == 'manual':

                    red_memb_prob = []
                    for star in memb_prob_avrg_sort:
                        if star[7] >= min_prob:
                            red_memb_prob.append(star)

                    if len(red_memb_prob) < 10:
                        print 'WARNING: less than 10 stars left after reducing'
                        print '         by membership prob. Using full list.'
                        red_memb_prob, min_prob = memb_prob_avrg_sort, 0.
            else:
                # Skip reduction process.
                red_memb_prob, min_prob = memb_prob_avrg_sort, 0.
        else:
            # Skip reduction process.
            red_memb_prob, min_prob = memb_prob_avrg_sort, 0.
    else:
        # Skip reduction process.
        red_memb_prob, min_prob = memb_prob_avrg_sort, 0.

    return red_memb_prob, min_prob