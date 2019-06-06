
import itertools
import warnings
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from os.path import join
from . import add_version_plot
from . import mp_decont_photom
from . import prep_plots


def main(
    npd, cld_c, pd, kde_cent, clust_rad, stars_out_c, cl_region_i,
    memb_probs_cl_region_i, memb_prob_avrg_sort, flag_decont_skip, n_memb_da,
    cl_reg_fit, cl_reg_no_fit, cl_reg_clean_plot, col_0_comb, mag_0_comb,
        err_lst, **kwargs):
    """
    """
    if 'C1' in pd['flag_make_plot']:
        fig = plt.figure(figsize=(30, 25))
        gs = gridspec.GridSpec(10, 12)
        add_version_plot.main(y_fix=.999)

        # Obtain plotting parameters and data.
        x_min, x_max, y_min, y_max = prep_plots.frame_max_min(
            cld_c['x'], cld_c['y'])
        x_zmin, x_zmax, y_zmin, y_zmax = prep_plots.frame_zoomed(
            x_min, x_max, y_min, y_max, kde_cent, clust_rad)
        coord, x_name, y_name = prep_plots.coord_syst(pd['coords'])
        v_min_mp, v_max_mp = prep_plots.da_colorbar_range(
            cl_reg_fit, cl_reg_no_fit)
        chart_fit_inv, chart_no_fit_inv, out_clust_rad =\
            prep_plots.da_find_chart(
                kde_cent, clust_rad, stars_out_c, x_zmin, x_zmax, y_zmin,
                y_zmax, cl_reg_fit, cl_reg_no_fit)

        # Decontamination algorithm plots.
        min_prob, bin_edges = cl_reg_clean_plot

        arglist = [
            # pl_mp_histo
            [gs, n_memb_da, memb_prob_avrg_sort, flag_decont_skip,
             cl_reg_fit, min_prob, pd['fld_clean_mode'], pd['fld_clean_bin']],
            # pl_chart_mps
            [gs, fig, x_name, y_name, coord, x_zmin, x_zmax, y_zmin,
             y_zmax, kde_cent, clust_rad, flag_decont_skip,
             v_min_mp, v_max_mp, chart_fit_inv, chart_no_fit_inv,
             out_clust_rad, pd['fld_clean_mode'], pd['fld_clean_bin']],
        ]
        for n, args in enumerate(arglist):
            mp_decont_photom.plot(n, *args)

        # Plot all 2D combinations of magnitudes and colors.
        mags_c, mags_i, cols_c, cols_i, colors_c, colors_i =\
            prep_plots.complSeparate(
                cl_region_i, memb_probs_cl_region_i, memb_prob_avrg_sort)
        mags_all = mags_c + mags_i
        j_gs = 0
        for i, col_c in enumerate(cols_c):
            col_i = cols_i[i]
            cols_all = list(col_c) + list(col_i)

            x_ax, y_ax = prep_plots.ax_names(
                pd['colors'][i], pd['filters'][0], 'mag')
            x_max_cmd, x_min_cmd, y_min_cmd, y_max_cmd =\
                prep_plots.diag_limits('mag', cols_all, mags_all)
            mp_decont_photom.pl_mps_incomp_diags(
                gs, fig, x_min_cmd, x_max_cmd, y_min_cmd, y_max_cmd, x_ax,
                y_ax, v_min_mp, v_max_mp, col_c, mags_c, colors_c,
                col_i, mags_i, colors_i, j_gs)
            j_gs += 1

        c_combs = list(itertools.combinations(range(len(cols_c)), 2))
        for i, j in c_combs:
            cols0_all = list(cols_c[i]) + list(cols_i[i])
            cols1_all = list(cols_c[j]) + list(cols_i[j])
            x_max_cmd, x_min_cmd, y_min_cmd, y_max_cmd =\
                prep_plots.diag_limits('col', cols0_all, cols1_all)
            x_ax, y_ax = prep_plots.ax_names(
                pd['colors'][i], pd['colors'][j], 'col')
            mp_decont_photom.pl_mps_incomp_diags(
                gs, fig, x_min_cmd, x_max_cmd, y_min_cmd, y_max_cmd, x_ax,
                y_ax, v_min_mp, v_max_mp, cols_c[i], cols_c[j], colors_c,
                cols_i[i], cols_i[j], colors_i, j_gs)
            j_gs += 1

        plot_colorbar, diag_fit_inv, diag_no_fit_inv = prep_plots.da_phot_diag(
            cl_reg_fit, cl_reg_no_fit, v_min_mp, v_max_mp)
        # Uses first magnitude and color defined
        x_max_cmd, x_min_cmd, y_min_cmd, y_max_cmd = prep_plots.diag_limits(
            'mag', col_0_comb, mag_0_comb)
        x_ax, y_ax = prep_plots.ax_names(
            pd['colors'][0], pd['filters'][0], 'mag')
        plot_observed_cluster(
            fig, gs, x_ax, y_ax, x_max_cmd, x_min_cmd, y_min_cmd, y_max_cmd,
            cl_reg_fit, cl_reg_no_fit, err_lst, v_min_mp,
            v_max_mp, plot_colorbar, diag_fit_inv, diag_no_fit_inv,
            pd['fld_clean_mode'], bin_edges)

        # Generate output file.
        plt.savefig(
            join(npd['output_subdir'], str(npd['clust_name']) +
                 '_C1.' + pd['plot_frmt']), dpi=pd['plot_dpi'],
            bbox_inches='tight')
        # Close to release memory.
        plt.clf()
        plt.close("all")

        print("<<Plots for C1 block created>>")
    else:
        print("<<Skip C1 block plot>>")


def plot_observed_cluster(
    fig, gs, x_ax, y_ax, x_max_cmd, x_min_cmd, y_min_cmd, y_max_cmd,
    cl_reg_fit, cl_reg_no_fit, err_lst, v_min_mp, v_max_mp, plot_colorbar,
        diag_fit_inv, diag_no_fit_inv, mode_fld_clean, bin_edges):
    """
    This function is called separately since we need to retrieve some
    information from it to plot that #$%&! colorbar.
    """
    err_bar = prep_plots.error_bars(
        cl_reg_fit + cl_reg_no_fit, x_min_cmd, err_lst)

    try:
        # pl_mps_phot_diag
        sca, trans = mp_decont_photom.pl_mps_phot_diag(
            gs, fig, x_min_cmd, x_max_cmd, y_min_cmd, y_max_cmd, x_ax,
            y_ax, v_min_mp, v_max_mp, diag_fit_inv, diag_no_fit_inv,
            err_bar, mode_fld_clean, bin_edges)
    except Exception:
        import traceback
        print(traceback.format_exc())
        print("  WARNING: error when plotting MPs on cluster's "
              "photometric diagram.")

    # Ignore warning issued by colorbar plotted in photometric diagram with
    # membership probabilities.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig.tight_layout()

    # Plot colorbar down here so tight_layout won't move it around.
    try:
        if plot_colorbar is True:
            import matplotlib.transforms as mts
            # Position and dimensions relative to the axes.
            x0, y0, width, height = [0.74, 0.93, 0.2, 0.04]
            # Transform them to get the ABSOLUTE POSITION AND DIMENSIONS
            Bbox = mts.Bbox.from_bounds(x0, y0, width, height)
            l, b, w, h = mts.TransformedBbox(Bbox, trans).bounds
            # Create the axes and the colorbar.
            cbaxes = fig.add_axes([l, b, w, h])
            cbar = plt.colorbar(
                sca, cax=cbaxes, ticks=[v_min_mp, v_max_mp],
                orientation='horizontal')
            cbar.ax.tick_params(labelsize=9)
    except Exception:
        import traceback
        print(traceback.format_exc())
        print("  WARNING: error when plotting colorbar on cluster's "
              "photometric diagram.")