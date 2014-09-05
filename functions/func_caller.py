# -*- coding: utf-8 -*-

from os.path import join, exists, isfile
from os import mkdir, rmdir, makedirs
import time
import shutil
import gc  # Garbage collector.
# Import files with defined functions.
from functions.get_data_semi import get_semi as g_s
from functions.get_phot_data import get_data as gd
from functions.trim_frame import trim_frame as t_f
from functions.get_center import get_center as g_c
from functions.get_histo_manual import manual_histo as mh
from functions.get_field_dens import field_dens as gfd
from functions.get_dens_prof import get_dens_prof as gdp
from functions.get_radius import get_clust_rad as gcr
from functions.get_king_prof import get_king_profile as gkp
from functions.err_accpt_rejct import err_accpt_rejct as ear
from functions.get_in_out import get_in_out as gio
from functions.get_integ_mag import integ_mag as g_i_m
from functions.get_members_number import get_memb_num as g_m_n
from functions.get_cont_index import cont_indx as g_c_i
from functions.get_regions import get_regions as g_r
from functions.decont_algor_bys import bys_da as dab
from functions.get_lf import lf
from functions.get_isoch_params import ip
from functions.reduce_membership import red_memb as rm
from functions.synth_cl_err import synth_clust_err as sce
from functions.best_fit_synth_cl import best_fit as bfsc
from functions.make_plots import make_plots as mp
from functions.add_data_output import add_data_output as a_d_o
from functions.cl_members_file import cluster_members_file as c_m_f

# Check if rpy2 package and R are installed, else skip get_p_value function.
from subprocess import Popen, PIPE
rpy2_inst, R_inst = True, True
try:
    from functions.get_p_value import get_pval as g_pv
except ImportError:
    rpy2_inst = False
# Now for R.
proc = Popen(["which", "R"], stdout=PIPE, stderr=PIPE)
exit_code = proc.wait()
if exit_code != 0:
    R_inst = False
r_flags = [R_inst, rpy2_inst]


def ocaat_funcs(myfile, sub_dir, out_file_name, gip_params):
    '''
    Container which holds the calls to all the functions.
    '''

    # Start timing this loop.
    start = time.time()

    # Unpack input parameters.
    mode, in_dirs, gd_params, gc_params, cr_params, kp_flag, er_params,\
    gr_params, pv_params, da_params, ps_params, bf_params, \
    sc_params, ga_params, rm_params, pl_params, flag_move_file, axes_params =\
    gip_params
    input_dir, output_dir, done_dir = in_dirs

    # Check mode.
    if mode not in {'auto', 'semi', 'manual'}:
        print "  WARNING: mode is incorrect. Default to 'manual'."
        mode = 'manual'

    # Generate output subdir.
    output_subdir = join(output_dir, sub_dir)
    # Check if subdir already exists, if not create it.
    if not exists(output_subdir):
        mkdir(output_subdir)

    # Store cluster's name
    clust_name = myfile[:-4]
    print 'Analizing cluster %s.' % (clust_name)

    # Get data from semi-data input file.
    mode, semi_return = g_s(input_dir, clust_name, mode)

    # Get cluster's photometric data from file.
    phot_data = gd(input_dir, sub_dir, myfile, gd_params)
    # If Manual mode is set, display frame and ask if it should be trimmed.
    phot_data = t_f(phot_data, mode)
    # Unpack coordinates, magnitude and color.
    x_data, y_data, mag_data, col1_data = phot_data[1], phot_data[2], \
    phot_data[3], phot_data[5]

    # Get cluster's center values and errors, filtered 2D hist, non-filtered
    # 2D hist, x,y bin centers and width of each bin
    # used
    center_params = g_c(x_data, y_data, mag_data, gc_params, mode, semi_return)
    # Unpack values from list.
    bin_width, h_not_filt, hist_xyedges, bin_center = center_params[0][0], \
    center_params[1], center_params[2], center_params[4]
    center_cl = [center_params[5][0][0], center_params[5][0][1]]

    # Obtain manual 2D histogram for the field with star's values attached
    # to each bin.
    H_manual = mh(phot_data, hist_xyedges)
    print 'Manual 2D histogram obtained.'

    # Get density profile
    rdp_params = gdp(h_not_filt, bin_center, bin_width)
    radii, ring_density = rdp_params[:2]
    print 'Radial density profile (RDP) calculated.'

    # Get field density value in stars/px^2.
    field_dens = gfd(ring_density)
    print 'Field density calculated (%0.5f stars/px^2).' % field_dens

    # Get cluster radius
    radius_params = gcr(phot_data, field_dens, cr_params, center_params,
        rdp_params, semi_return, mode, bin_width)
    clust_rad = radius_params[0]

    # Get King profiles based on the density profiles.
    kp_params = gkp(kp_flag, clust_rad, field_dens, radii, ring_density)

    # Get approximate number of cluster's members.
    n_c, flag_num_memb_low, a_clust, n_clust = g_m_n(field_dens, clust_rad,
        rdp_params, bin_width)
    print 'Approximate number of members in cluster obtained (%d).' % (n_c)

    # Get contamination index.
    cont_index = g_c_i(field_dens, a_clust, n_clust)
    print 'Contamination index obtained (%0.2f).' % cont_index

    # Accept and reject stars based on their errors.
    acpt_stars, rjct_stars, err_plot, err_flags, err_pck, er_params = \
    ear(phot_data, axes_params, er_params, mode, semi_return)

    # Get stars in and out of cluster's radius.
    cl_region, stars_out, stars_in_rjct, stars_out_rjct = gio(center_cl,
        clust_rad, acpt_stars, rjct_stars)
    print "Stars separated in/out of cluster's boundaries."

    # Field regions around the cluster's center.
    flag_area_stronger, cl_reg_big, field_region = g_r(bin_center,
        bin_width, h_not_filt, clust_rad, H_manual, cl_region, stars_out,
        gr_params)
    print 'Field stars regions obtained (%d).' % len(field_region)

    # Get the luminosity function and completeness level for each magnitude
    # bin. The completeness will be used by the isochrone/synthetic cluster
    # fitting algorithm.
    lum_func, completeness = lf(flag_area_stronger, mag_data, cl_region,
        field_region)
    print 'LF and Completeness magnitude levels obtained.'

    # Calculate integrated magnitude.
    integr_return = g_i_m(cl_region, field_region, axes_params,
        flag_area_stronger)

    # Only run if both R and rpy2 packages are installed.
    if all(f is True for f in r_flags):
        # R and rpy2 package are installed, call function.
        # Get physical cluster probability based on p_values distribution.
        pval_test_params, flag_pval_test = g_pv(cl_region, field_region,
            col1_data, mag_data, pv_params, flag_area_stronger)
    else:
        if pv_params[0]:
            # Something is not installed and function was told to run.
            print '  WARNING: R or rpy2 not installed. Skipping function.'
        else:
            # Something is not installed, but function was told not to run.
            print 'Skipping p-value function.'
        flag_pval_test, pval_test_params = False, [-1., [], [], [], [], [], []]

    # Apply decontamination algorithm if at least one equal-sized field region
    # was found around the cluster.
    print 'Applying decontamination algorithm.'
    decont_algor_return = dab(flag_area_stronger, cl_region, field_region,
                            clust_name, sub_dir, da_params)
    memb_prob_avrg_sort = decont_algor_return[0]

    # Create data file with membership probabilities.
    c_m_f(output_dir, sub_dir, clust_name, memb_prob_avrg_sort)
    print 'Membership probabilities saved to file.'

    # Store all isochrones in all the metallicity files in isoch_list.
    # Store metallicity values and isochrones ages between the allowed
    # ranges in isoch_ma; extinction and distance modulus values in isoch_ed.
    # isoch_list, isoch_ma, isoch_ed = ip_list
    # Only read files if best fit process is set to run.
    # bf_flag = bf_params[0]
    ip_list = ip(ps_params, bf_params[0])

    # Reduce number of stars in cluster according to a lower membership
    # probability or magnitude limit.
    red_return = rm(decont_algor_return, bf_params, rm_params)
    red_memb_prob = red_return[0]

    # Obtain exponential error function parameters to use by the
    # synthetic cluster creation function.
    err_lst = sce(phot_data, err_pck)
    # Obtain best fitting parameters for cluster.
    bf_return = bfsc(err_lst, red_memb_prob, completeness, ip_list, bf_params,
        sc_params, ga_params, ps_params)

    # New name for cluster? Useful when there's a single photometric file
    # with multiple clusters in it.
    if mode == 'manual':
        wrong_answer = True
        while wrong_answer:
            answer_rad = raw_input('New name for cluster? (y/n) ')
            if answer_rad == 'n':
                wrong_answer = False
            elif answer_rad == 'y':
                new_name = str(raw_input('Input new name: '))
                clust_name = new_name
                wrong_answer = False
            else:
                print 'Wrong input. Try again.\n'

    # Add cluster data and flags to output file
    a_d_o(out_file_name, sub_dir, output_dir, clust_name, center_params,
        radius_params, kp_params, cont_index, n_c, pval_test_params[0],
        integr_return, err_flags, flag_num_memb_low, bf_return)
    print 'Data added to output file.'

    # Make plots
    if pl_params[0]:
        mp(output_subdir, clust_name, x_data, y_data, center_params, rdp_params,
            field_dens, radius_params, cont_index, mag_data, col1_data,
            err_plot, err_flags, kp_params, cl_region, stars_out,
            stars_in_rjct, stars_out_rjct, integr_return, n_c,
            flag_area_stronger, cl_reg_big, field_region, flag_pval_test,
            pval_test_params, memb_prob_avrg_sort, lum_func, completeness,
            da_params, bf_params, red_return, err_lst, bf_return, ga_params,
            er_params, axes_params, ps_params, pl_params)
        print 'Plots created.'

    # Move file to 'done' dir.
    if flag_move_file:
        dst_dir = join(done_dir, sub_dir)
        # If the sub-dir doesn't exist, create it before moving the file.
        if not exists(dst_dir):
            makedirs(dst_dir)
        shutil.move(join(input_dir, sub_dir, myfile), dst_dir)
        # Also move *memb_data.dat file if it exists.
        if isfile(join(input_dir, sub_dir, clust_name + '_memb.dat')):
            shutil.move(join(input_dir, sub_dir, clust_name + '_memb.dat'),
                dst_dir)
        # If sub-dir left behind is empty, remove it.
        try:
            rmdir(join(input_dir, sub_dir))
        except OSError:
            # Sub-dir not empty, skip.
            pass
        print 'Photometric data file moved.'

    elapsed = time.time() - start
    m, s = divmod(elapsed, 60)
    print 'End of analysis for %s in %dm %02ds.\n' % (clust_name, m, s)

    # Force the Garbage Collector to release unreferenced memory.
    gc.collect()