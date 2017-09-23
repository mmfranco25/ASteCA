
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from os.path import join
import mp_structure
import add_version_plot
import prep_plots


#############################################################
# # Timer function: http://stackoverflow.com/a/21860100/1391441
# from contextlib import contextmanager
# import time
# @contextmanager
# def timeblock(label):
#     start = time.clock()
#     try:
#         yield
#     finally:
#         end = time.clock()
#         print ('{} elapsed: {}'.format(label, end - start))
#############################################################

def main(
        npd, cld, pd, kde_cent, kde_plot, K_cent_dens, clust_rad,
        e_rad, poisson_error, stars_out_rjct, field_regions, bin_cent,
        bin_width, hist_2d_g, core_rad, e_core, tidal_rad, e_tidal,
        K_conct_par, flag_2pk_conver, flag_3pk_conver, radii, rdp_points,
        field_dens, cont_index, cl_region, flag_no_fl_regs, **kwargs):
    '''
    Make A2 block plots.
    '''
    if 'A2' in pd['flag_make_plot']:
        # figsize(x1, y1), GridSpec(y2, x2) --> To have square plots: x1/x2 =
        # y1/y2 = 2.5
        fig = plt.figure(figsize=(30, 25))
        gs = gridspec.GridSpec(10, 12)
        add_version_plot.main()

        # Obtain plotting parameters and data.
        x_min, x_max, y_min, y_max = prep_plots.frame_max_min(
            cld['x'], cld['y'])
        asp_ratio = prep_plots.aspect_ratio(x_min, x_max, y_min, y_max)
        coord, x_name, y_name = prep_plots.coord_syst(pd['coords'])
        x_zmin, x_zmax, y_zmin, y_zmax = prep_plots.frame_zoomed(
            x_min, x_max, y_min, y_max, kde_cent, clust_rad)
        x_data_z, y_data_z, mag_data_z = prep_plots.zoomed_frame(
            cld['x'], cld['y'], cld['mags'], x_zmin, x_zmax, y_zmin, y_zmax)
        st_sizes_arr = prep_plots.star_size(cld['mags'][0])
        st_sizes_arr_z = prep_plots.star_size(mag_data_z)

        # Structure plots.
        arglist = [
            # pl_center: 2D Gaussian convolved histogram.
            [gs, fig, asp_ratio, x_name, y_name, coord, bin_cent, clust_rad,
                bin_width, hist_2d_g[1]],
            # pl_full_frame: x,y finding chart of full frame.
            [gs, fig, x_name, y_name, coord, x_min, x_max, y_min, y_max,
             asp_ratio, kde_cent, clust_rad, cld['x'], cld['y'],
             st_sizes_arr, core_rad, e_core, tidal_rad, e_tidal, K_conct_par,
             flag_2pk_conver, flag_3pk_conver],
            # pl_rad_dens: Radial density plot.
            [gs, pd['run_mode'], radii, rdp_points, field_dens, coord,
             npd['clust_name'], clust_rad, e_rad, poisson_error, bin_width,
             core_rad, e_core, tidal_rad, e_tidal, K_cent_dens,
             flag_2pk_conver, flag_3pk_conver],
            # pl_zoom_frame: Zoom on x,y finding chart.
            [gs, fig, x_name, y_name, coord, x_zmin, x_zmax, y_zmin, y_zmax,
                cont_index, kde_plot, x_data_z, y_data_z,
                st_sizes_arr_z, kde_cent, clust_rad],
            # pl_cl_fl_regions: Cluster and field regions defined.
            [gs, fig, x_name, y_name, coord, x_min, x_max, y_min, y_max,
                asp_ratio, kde_cent, clust_rad, field_regions, cl_region,
                flag_no_fl_regs]
        ]
        for n, args in enumerate(arglist):
            # with timeblock("{}".format(n)):
            mp_structure.plot(n, *args)

        # Generate output file.
        fig.tight_layout()
        plt.savefig(
            join(npd['output_subdir'], str(npd['clust_name']) +
                 '_A2.' + pd['plot_frmt']), dpi=pd['plot_dpi'],
            bbox_inches='tight')
        # Close to release memory.
        plt.clf()
        plt.close("all")

        print("<<Plots for A2 block created>>")
    else:
        print("<<Skip A2 block plot>>")