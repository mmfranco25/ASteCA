
import time
import gc  # Garbage collector.
#
from inp import names_paths
from inp import get_data_semi
from inp import get_data
# from structure import trim_frame  # DEPRECATED
from structure import histo_2d
from structure import xy_density
from structure import center
from structure import radial_dens_prof
from structure import field_density
from structure import radius
from structure import cluster_area
from structure import numb_stars_clust
from structure import contamination_index
from structure import king_profile
from errors import err_accpt_rejct
from structure import stars_in_out_cl_reg
from structure import field_regions
from errors import err_range_avrg
#
from phot_analysis import luminosity
from phot_analysis import integrated_mag
from phot_analysis import kde_pvalue
from phot_analysis import members_number
#
from decont_algors import decont_algors
from decont_algors import members_N_compare
from decont_algors import cl_region_clean
#
from out import cluster_members_file
from best_fit import best_fit_synth_cl
from out import synth_cl_file
from out import create_out_data_file
from errors import error_round
#
from out import add_data_output
from out import make_A1_plot
from out import make_A2_plot
from out import make_B_plot
from out import make_C_plot
from out import make_D1_plot
from out import make_D2_plot
from out import top_tiers
from out import done_move


def main(cl_file, pd):
    '''
    Call each function sequentially. Four dictionaries are passed around:

    pd : contains all the input parameters stored in 'params_input.dat'.
    This dictionary is only modified when the 'semi_input.dat' file is read.

    npd : names and paths for the cluster and all the files generated.
    Generated by 'names_paths' and never modified.

    cld : read cluster data. Generated by 'get_data'
    DEPRECATED: and modified by 'trim_frame', if the frame is manually trimmed.

    clp : contains all the information about the cluster gathered by the
    functions applied. Modified constantly throughout the code.

    '''

    # Start timing this loop.
    start = time.time()

    # File names (n) and paths (p) dictionary (d).
    npd = names_paths.main(cl_file, **pd)

    # Get data from semi-data input file. Add to dictionary.
    pd = get_data_semi.main(pd, **npd)

    # Cluster's data from file, as dictionary. Obtain both incomplete (ie: with
    # nan values) and complete (all rows contain valid data) dictionaries.
    cld_i, cld_c = get_data.main(npd, **pd)

    # DEPRECATED (at least for now, 08/05/18)
    # If Manual mode is set, display frame and ask if it should be trimmed.
    # cld = trim_frame.main(cld, **pd)

    # Obtain 2D coordinates histogram for the observed frame.
    # Return cluster's parameters dictionary 'clp'.
    clp = histo_2d.main(**cld_i)

    # Gaussian filtered 2D x,y histograms.
    clp = xy_density.main(clp, **pd)

    make_A1_plot.main(npd, cld_i, pd, **clp)

    # Cluster's center coordinates and errors.
    clp = center.main(cld_i, clp, **pd)

    # Density profile
    clp = radial_dens_prof.main(clp)

    # Field density value in stars/<area unit>.
    clp = field_density.main(clp, **pd)

    # Cluster radius
    clp = radius.main(cld_i, clp, **pd)

    # Cluster's area and total number of stars within the cluster region.
    clp = cluster_area.main(clp, **cld_i)

    # Contamination index.
    clp = contamination_index.main(clp, **cld_i)

    # King profiles based on the density profiles.
    clp = king_profile.main(clp, **pd)

    # ^ All the functions above use the *incomplete* dataset 'cld_i'
    #   (ie: the one that contains 'nan' values).

    # These three functions are applied for both datasets since we need the
    # 'cl_region' and 'field_regions' parameters with *incomplete* data to be
    # used by the Bayesian DA, and the parameters obtained with the *complete*
    # dataset for the rest of the functions.
    # The incomplete 'cl_region' and 'field_regions' parameters are also used
    # by the A2 plot (for the cluster+field regions plot)
    for i_c, cld_x in (('incomp', cld_i), ('comp', cld_c)):
        print("Processing {}lete dataset:".format(i_c))

        # Accept and reject stars based on their errors.
        clp = err_accpt_rejct.main(i_c, cld_x, clp, **pd)

        # Stars in and out of cluster's radius.
        clp = stars_in_out_cl_reg.main(i_c, clp)

        # Field regions around the cluster's center.
        clp = field_regions.main(i_c, clp, **pd)

    make_A2_plot.main(npd, cld_i, pd, **clp)
    import pdb; pdb.set_trace()  # breakpoint 5e3a2f53 //


    # v Those below use the *complete* dataset, ie: no 'nan' values.

    # Obtain exponential fit for the errors.
    clp = err_range_avrg.main(clp)

    # Luminosity function and completeness level for each magnitude bin.
    clp = luminosity.main(clp, **cld)

    # Calculate integrated magnitude.
    clp = integrated_mag.main(clp, **pd)

    # Physical cluster probability based on p_values distribution.
    clp = kde_pvalue.main(clp, **pd)

    # Approximate number of cluster's members.
    clp = members_number.main(clp)  # Uses *not complete* dataset TODO

    make_B_plot.main(npd, cld, pd, **clp)

    # Apply decontamination algorithm.
    clp = decont_algors.main(clp, npd, **pd)

    # Obtain members parameter.
    clp = members_N_compare.main(clp)  # <-- DEPRECATE? TODO

    # Remove stars from the observed cluster according to a selected method.
    clp = cl_region_clean.main(clp, **pd)

    make_C_plot.main(npd, cld, pd, **clp)

    # Create data file with membership probabilities.
    cluster_members_file.main(clp, **npd)

    # Obtain best fitting parameters for cluster.
    clp = best_fit_synth_cl.main(clp, **pd)

    # Create output synthetic cluster file if one was found
    clp = synth_cl_file.main(clp, npd, **pd)

    # Create template output data file in /output dir.
    create_out_data_file.main(npd)

    # Round fundamental parameters fitted and their errors
    clp = error_round.fundParams(clp)

    # Add cluster data and flags to output file
    add_data_output.main(npd, pd, **clp)

    # Plot result of best match algorithm.
    make_D1_plot.main(npd, pd, **clp)

    # Plot final best match found.
    make_D2_plot.main(npd, cld, pd, **clp)

    # Plot top tiers models and save to file.
    top_tiers.main(npd, cld, pd, **clp)

    # Move file to 'done' dir (if flag is set).
    done_move.main(pd, **npd)

    elapsed = time.time() - start
    m, s = divmod(elapsed, 60)
    if m > 60:
        h, m = divmod(m, 60)
        t = "{:.0f}h {:.0f}m {:.0f}s".format(h, m, s)
    else:
        t = "{:.0f}m {:.0f}s".format(m, s)
    print('End of analysis for {} in {}.\n'.format(npd['clust_name'], t))

    # Force the Garbage Collector to release unreferenced memory.
    gc.collect()
