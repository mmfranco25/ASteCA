
import numpy as np
from scipy import stats
from ..out import prep_plots
from .xy_density import cent_bin as center_bin
from ..inp.get_data import coordsProject


def main(
    cld_i, clp, coords, project, run_mode, center_bw, cl_cent_semi,
        cl_rad_semi, cent_flag_semi, **kwargs):
    """
    Obtains the center of the putative cluster. Returns the center values
    along with its errors and several arrays related to histograms, mainly for
    plotting purposes.
    """

    coord = prep_plots.coord_syst(coords)[0]

    if run_mode == 'auto' or run_mode == 'semi' and cent_flag_semi == 0:

        # Restrict the KDE to a smaller area (to improve performance).
        radius = 0.25 * min(
            np.nanmax(cld_i['x']) - np.nanmin(cld_i['x']),
            np.nanmax(cld_i['y']) - np.nanmin(cld_i['y']))

        # Obtain center coordinates as the maximum KDE value. Use the
        # approximate center obtained with the full frame and the given
        # bandwidth.
        cent = clp['kde_approx_cent']
        kde_cent, kde_plot = kde_center_zoom(
            cld_i['x'], cld_i['y'], cent, radius)

        # Find bin where the center xy coordinates are located.
        bin_cent = center_bin(clp['xedges'], clp['yedges'], kde_cent)

        print("Auto center found (bw={:g}): ({:g}, {:g}) {c}".format(
            center_bw, kde_cent[0], kde_cent[1], c=coord))

    elif run_mode == 'semi' and cent_flag_semi in [1, 2]:
        # Search for new center values using the center coordinates
        # and radius given as initial values.

        # De-project center coordinates if needed.
        x0, y0, _, _ = coordsProject(
            cl_cent_semi[0], cl_cent_semi[1], coords, project,
            clp['x_offset'], clp['y_offset'])

        # Obtain KDE center using the 'semi' values.
        kde_cent, kde_plot = kde_center_zoom(
            cld_i['x'], cld_i['y'], (x0, y0), cl_rad_semi)

        # Re-write center values if fixed in semi input file.
        if cent_flag_semi == 1:
            if coords == 'deg' and project:
                x_cent = (kde_cent[0] / np.cos(
                    np.deg2rad(kde_cent[1] + clp['y_offset']))) +\
                    clp['x_offset']
            else:
                x_cent = kde_cent[0]

            print("Semi center found: ({:g}, {:g}) {}".format(
                x_cent, kde_cent[1] + clp['y_offset'], coord))
        else:
            kde_cent = (x0, y0)
            print("Semi center fixed: ({:g}, {:g}) {}".format(
                *cl_cent_semi, coord))

        # Find bin where the center xy coordinates are located.
        bin_cent = center_bin(clp['xedges'], clp['yedges'], kde_cent)

    # DEPRECATED May 2019
    # # If Manual mode is set, display center and ask the user to accept it or
    # # input new one.
    # elif run_mode == 'manual':

    #     # Restrict the KDE to a smaller area (to improve performance).
    #     radius = 0.25 * min(np.ptp(cld_i['x']), np.ptp(cld_i['y']))
    #     kde_cent, kde_plot = kde_center_zoom(
    #         cld_i['x'], cld_i['y'], clp['kde_approx_cent'], radius)
    #     bin_cent = center_bin(clp['xedges'], clp['yedges'], kde_cent)

    #     # Show plot with center obtained. Use main magnitude.
    #     display_cent.main(
    #         cld_i['x'], cld_i['y'], cld_i['mags'][0], kde_cent, bin_cent,
    #         clp['hist_2d_g'][1], coords)
    #     plt.show()
    #     # No KDE plot is 'manual' mode is used.
    #     kde_plot = []

    #     # Ask if the user accepts the center coordinates found, or if new ones
    #     # should be used.
    #     while True:
    #         answer_cen = raw_input('Input new center values? (y/n) ')
    #         if answer_cen == 'n':
    #             print('Value accepted.')
    #             break
    #         elif answer_cen == 'y':
    #             kde_cent = []
    #             try:
    #                 kde_cent.append(float(raw_input('x_center: ')))
    #                 kde_cent.append(float(raw_input('y_center: ')))
    #                 # Store center bin coords for the filtered hist.
    #                 bin_cent = center_bin(
    #                     clp['xedges'], clp['yedges'], kde_cent)
    #                 flag_center_manual = True  # <-- ??
    #                 break
    #             except Exception:
    #                 print("Sorry, input is not valid. Try again")
    #         else:
    #             print("Sorry, input is not valid. Try again")

    # Add data to dictionary.
    center_params = {
        'kde_cent': kde_cent, 'kde_plot': kde_plot, 'bin_cent': bin_cent}
    clp.update(center_params)

    return clp


def kde_center_zoom(x_data, y_data, kde_approx_cent, radius):
    '''
    Find the KDE maximum value pointing to the center coordinates.
    '''

    # Unpack approximate center values.
    x_cent_pix, y_cent_pix = kde_approx_cent

    # Generate zoom around approx center value to speed things up.
    xmin_z, xmax_z = x_cent_pix - radius, x_cent_pix + radius
    ymin_z, ymax_z = y_cent_pix - radius, y_cent_pix + radius
    ext_range = [xmin_z, xmax_z, ymin_z, ymax_z]
    # Use reduced region around the center.
    x_zoom, y_zoom = [], []
    for indx, star_x in enumerate(x_data):
        if xmin_z < star_x < xmax_z and ymin_z < y_data[indx] < ymax_z:
            x_zoom.append(star_x)
            y_zoom.append(y_data[indx])
    values = np.vstack([x_zoom, y_zoom])

    # Check if there is at least one star selected here.
    if not values.any():
        raise ValueError(
            "ERROR: cluster region is empty and no center value\n"
            "could be estimated. Check that x,y columns are correct\n"
            "in 'params_input.dat' file.")

    # Obtain Gaussian KDE.
    kernel = stats.gaussian_kde(values)
    # Grid density (number of points).
    gd = 100
    gd_c = complex(0, gd)
    # Define x,y grid.
    x_grid, y_grid = np.mgrid[xmin_z:xmax_z:gd_c, ymin_z:ymax_z:gd_c]
    positions = np.vstack([x_grid.ravel(), y_grid.ravel()])
    # Evaluate kernel in grid positions.
    k_pos = kernel(positions)
    # Coordinates of max value in x,y grid (ie: center position).
    kde_cent = positions.T[np.argmax(k_pos)]

    # Pass for plotting.
    kde_plot = [ext_range, x_grid, y_grid, k_pos]

    return kde_cent, kde_plot
