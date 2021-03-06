
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib import patches as mpatches
from itertools import cycle
from ..structure.king_profile import KingProf as kpf


def pl_rad_find(
    gs, plot_style, coord, clust_rad, e_rad, rad_rads, rad_N_membs,
        rad_N_field, rad_CI):
    """
    Radius estimation plot.
    """
    # Convert from deg to arcmin if (ra,dec) were used.
    if coord == 'deg':
        rad_rads = np.array(rad_rads) * 60.
        clust_rad, e_rad = clust_rad * 60., e_rad * 60.
        coord2 = 'arcmin'
    else:
        coord2 = 'px'

    # Cut when N_nembs = 0
    try:
        icut = np.where(rad_N_membs == 0.)[0][0]
        if icut == 0:
            icut = len(rad_N_membs)
        else:
            # Use 30 points since the number of radii values in
            # radius.rdpAreasDists() is hardcoded to 300.
            icut = icut + 30
    except IndexError:
        icut = len(rad_N_membs)
    rad_rads, rad_N_membs, rad_N_field, rad_CI = rad_rads[:icut],\
        rad_N_membs[:icut], rad_N_field[:icut], rad_CI[:icut]

    ax = plt.subplot(gs[0:2, 0:2])
    plt.xlabel(r'radius $[{}]$'.format(coord2))
    plt.ylabel(r"$N_{memb}\;|\;N_{field}\;|\;CI$")
    if plot_style == 'asteca':
        ax.grid()

    plt.plot(rad_rads, rad_N_membs, c='g', label=r'$N_{memb}$')
    plt.plot(rad_rads, rad_N_field, c='b', ls='--', label=r'$N_{field}$')
    # ymin, ymax = ax.get_ylim()

    plt.plot(rad_rads, rad_CI, ls=':', c='k', label='CI')
    plt.axvline(x=clust_rad, lw=1.5, color='r', label=r"$r_{cl}$")
    if not np.isnan(e_rad[0]):
        plt.axvspan((e_rad[0]), (e_rad[1]), facecolor='grey', alpha=0.25)
    # Legends.
    leg = plt.legend(fancybox=True)
    leg.get_frame().set_alpha(0.7)

    xmin, xmax = ax.get_xlim()
    plt.xlim(max(xmin, 0.), xmax)
    plt.ylim(0., 1.02)
    # plt.ylim(ymin, ymax)


def pl_rad_dens(
    gs, plot_style, coord, rdp_radii, rdp_points, rdp_stddev, field_dens,
    e_fdens, clust_rad, e_rad, kp_flag, KP_Bys_rc, KP_Bys_rt, KP_cent_dens,
        KP_conct_par):
    """
    Radial density plot.
    """

    # Convert from deg to arcmin if (ra,dec) were used.
    if coord == 'deg':
        rdp_radii = np.array(rdp_radii) * 60.
        clust_rad, e_rad = clust_rad * 60., e_rad * 60.
        KP_Bys_rc, KP_Bys_rt = KP_Bys_rc * 60., KP_Bys_rt * 60.
        field_dens, e_fdens, KP_cent_dens = field_dens / 3600.,\
            e_fdens / 3600., KP_cent_dens / 3600.
        rdp_points = np.array(rdp_points) / 3600.
        rdp_stddev = np.array(rdp_stddev) / 3600.
        coord2 = 'arcmin'
    else:
        coord2 = 'px'

    ax = plt.subplot(gs[0:2, 2:6])
    # Get max and min values in x,y
    x_min = max(min(rdp_radii) - (max(rdp_radii) / 20.), 0)
    x_max = min(max(rdp_radii) + (max(rdp_radii) / 20.), 3. * clust_rad)

    N_h = int(.5 * len(rdp_points))
    delta_total = (max(rdp_points) - field_dens)
    delta_backg = 0.1 * delta_total
    y_min = max((field_dens - delta_backg) -
                (max(rdp_points[:N_h]) - min(rdp_points[:N_h])) / 10., 0)
    y_max = max(rdp_points[:N_h]) + (
        max(rdp_points[:N_h]) - min(rdp_points[:N_h])) / 10.
    # Set plot limits
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)

    plt.xlabel(r'radius $[{}]$'.format(coord2))
    plt.ylabel(r"$\rho$ $[st/{}^{{2}}]$".format(coord2))
    ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    if plot_style == 'asteca':
        ax.grid()

    # Legend texts
    r_frmt = '{:.0f}' if coord2 == 'px' else '{:.2f}'
    t_rad = r"$r_{{{}}}=" + r_frmt + r"_{{" + r_frmt + r"}}^{{" +\
        r_frmt + r"}}\,[{}]$"

    # Plot density profile
    ax.plot(rdp_radii, rdp_points, marker='o', ms=5, lw=0., zorder=3,
            label="RDP")
    # Plot error bars
    plt.errorbar(
        rdp_radii, rdp_points, yerr=rdp_stddev, fmt='none', ecolor='grey',
        lw=1., zorder=1)

    # Plot background level.
    ax.hlines(y=field_dens, xmin=0, xmax=max(rdp_radii), color='k', ls='--',
              zorder=5)
    if not np.isnan(e_fdens):
        ax.hlines(
            y=field_dens - e_fdens, xmin=0, xmax=max(rdp_radii),
            color='k', ls=':', zorder=5)
        ax.hlines(
            y=field_dens + e_fdens, xmin=0, xmax=max(rdp_radii),
            color='k', ls=':', zorder=5)
    # Plot radius.
    y_mid_point = (y_max + y_min) * .5
    ax.vlines(x=clust_rad, ymin=field_dens, ymax=y_mid_point, lw=1.5,
              color='r', label=t_rad.format(
                  "cl", clust_rad, e_rad[0], e_rad[1], coord2), zorder=5)
    # Plot radius error zone.
    if not np.isnan(e_rad[0]):
        plt.axvspan(e_rad[0], e_rad[1], facecolor='grey', alpha=0.25)

    # Plot King profile.
    if kp_flag:
        txts = [
            'King prof ({:.2f})'.format(KP_conct_par),
            t_rad.format(
                "c", KP_Bys_rc[3], KP_Bys_rc[0], KP_Bys_rc[2], coord2),
            t_rad.format("t", KP_Bys_rt[1], KP_Bys_rt[0], KP_Bys_rt[2], coord2)
        ]
        # Plot curve. Values outside of rt contribute 'fd'.
        kpf_xvals = np.linspace(rdp_radii[0], KP_Bys_rt[1], 100)
        kpf_yvals = KP_cent_dens * kpf(
            kpf_xvals, KP_Bys_rc[3], KP_Bys_rt[3]) + field_dens
        ax.plot(kpf_xvals, kpf_yvals, 'g--', label=txts[0], lw=2., zorder=3)
        # Core radius
        rc_ymax = KP_cent_dens * kpf(
            KP_Bys_rc[3], KP_Bys_rc[3], KP_Bys_rt[3]) + field_dens
        ax.vlines(
            x=KP_Bys_rc[3], ymin=field_dens, ymax=rc_ymax, label=txts[1],
            color='g', linestyles=':', lw=2., zorder=5)
        # Tidal radius
        ax.vlines(x=KP_Bys_rt[3], ymin=field_dens, ymax=y_mid_point,
                  label=txts[2], color='g')

    # get handles
    handles, labels = ax.get_legend_handles_labels()
    # use them in the legend
    ax.legend(handles, labels, loc='upper center', numpoints=2)

    #
    # Log-log plot
    axins = inset_axes(ax, width=2.5, height=2.5)
    if plot_style == 'asteca':
        axins.grid(which='both')

    # plt.xlabel(r'log(radius) $[{}]$'.format(coord2), fontsize=8)
    # plt.ylabel(r"log($\rho$) $[st/{}^{{2}}]$".format(coord2), fontsize=8)

    axins.scatter(rdp_radii, rdp_points, s=5, zorder=5)
    axins.hlines(y=field_dens, xmin=min(rdp_radii), xmax=max(rdp_radii),
                 color='k', ls='--', zorder=5)
    # if not np.isnan(e_fdens):
    #     axins.hlines(
    #         y=field_dens - e_fdens, xmin=min(rdp_radii),
    #         xmax=max(rdp_radii), color='k', ls=':', zorder=5)
    #     axins.hlines(
    #         y=field_dens + e_fdens, xmin=min(rdp_radii),
    #         xmax=max(rdp_radii), color='k', ls=':', zorder=5)

    # Plot King profile.
    if kp_flag:
        axins.plot(kpf_xvals, kpf_yvals, 'g--', lw=1., zorder=3)
        axins.vlines(
            x=KP_Bys_rc[3], ymin=field_dens, ymax=rc_ymax, color='g',
            linestyles=':', lw=1.)
        axins.vlines(
            x=KP_Bys_rt[3], ymin=field_dens, ymax=y_mid_point, color='g', lw=1)
    else:
        axins.vlines(
            x=clust_rad, ymin=field_dens, ymax=y_mid_point, lw=1.5, color='r',
            zorder=10)

    axins.set_xscale('log')
    axins.set_yscale('log')
    y0, y1 = axins.set_ylim()
    axins.set_ylim(y0, y_max)


def pl_zoom_frame(
    gs, fig, x_name, y_name, coord, x_zmin, x_zmax, y_zmin, y_zmax, cont_index,
    x_data, y_data, st_sizes_arr, kde_cent, clust_rad, KP_Bys_rc,
        KP_Bys_rt, KP_Bys_ecc, KP_Bys_theta, frac_cl_area, kp_flag):
    """
    Zoom on x,y finding chart.
    """
    ax = plt.subplot(gs[2:4, 0:2])

    # Force square plot.
    ax.set_aspect('equal')
    # Set plot limits.
    plt.xlim(x_zmin, x_zmax)
    plt.ylim(y_zmin, y_zmax)
    if coord == 'deg':
        # If RA is used, invert axis.
        ax.invert_xaxis()
    # Set axis labels
    plt.xlabel('{} ({})'.format(x_name, coord))
    plt.ylabel('{} ({})'.format(y_name, coord))

    # Plot radius.
    circle = plt.Circle((kde_cent[0], kde_cent[1]), clust_rad, color='r',
                        fill=False, lw=1.5, zorder=5)
    # Stars inside the cluster
    N_in = 0
    for x, y in zip(*[x_data, y_data]):
        if np.sqrt((x - kde_cent[0])**2 + (y - kde_cent[1])**2) <= clust_rad:
            N_in += 1

    ax.set_title(
        (r"$A_{{fr}}$={:.0f}%, $N_{{r<r_{{cl}}}}$={}, "
            "[$CI = {:.2f}$] (phot incomp)").format(
            100. * frac_cl_area, N_in, cont_index))
    fig.gca().add_artist(circle)

    # Core and tidal radii
    if kp_flag:
        # Plot tidal radius.
        rt_mode, ecc_mode, theta_mode = KP_Bys_rt[4], KP_Bys_ecc[4],\
            KP_Bys_theta[4]
        b = rt_mode * np.sqrt(1. - ecc_mode**2)
        ellipse = mpatches.Ellipse(
            xy=kde_cent, width=2. * rt_mode, height=2. * b,
            angle=np.rad2deg(theta_mode), facecolor='None', edgecolor='g',
            linewidth=1.5, transform=ax.transData)
        # circle = plt.Circle(
        #     (kde_cent[0], kde_cent[1]), KP_Bys_rt[3], color='g', fill=False,
        #     lw=1.5)
        fig.gca().add_artist(ellipse)
        # Plot core radius.
        rc_mode = KP_Bys_rc[4]
        # circle = plt.Circle(
        #     (kde_cent[0], kde_cent[1]), KP_Bys_rc[3], color='g',
        #     fill=False, ls='dashed', lw=1.)
        b = rc_mode * np.sqrt(1. - ecc_mode**2)
        ellipse = mpatches.Ellipse(
            xy=kde_cent, width=2. * rc_mode, height=2. * b,
            angle=np.rad2deg(theta_mode), facecolor='None', edgecolor='g',
            ls='dashed', linewidth=1.5, transform=ax.transData)
        fig.gca().add_artist(ellipse)

    # # Plot contour levels if it was obtained.
    # if kde_plot:
    #     ext_range, x, y, k_pos = kde_plot
    #     # Number of contour lines depends on how large the cluster area is
    #     # compared with the area where the positional KDE was obtained.
    #     frac_xy = (ext_range[1] - ext_range[0]) / (2. * clust_rad)
    #     if frac_xy <= 1.5:
    #         c_lines = 5
    #     elif 1.5 < frac_xy <= 2.:
    #         c_lines = 10
    #     elif 2. < frac_xy <= 2.5:
    #         c_lines = 15
    #     elif 2.5 < frac_xy <= 3.:
    #         c_lines = 20
    #     elif 3 < frac_xy <= 3.5:
    #         c_lines = 25
    #     elif 3.5 < frac_xy:
    #         c_lines = 30
    #     kde = np.reshape(k_pos.T, x.shape)
    #     plt.contour(x, y, kde, c_lines, colors='b', linewidths=0.6)

    # Plot stars.
    plt.scatter(x_data, y_data, marker='o', c='black', s=st_sizes_arr,
                zorder=1)
    # Plot center.
    plt.scatter(kde_cent[0], kde_cent[1], color='r', s=40, lw=1.5,
                marker='x', zorder=5)


def pl_dens_map(
    gs, fig, asp_ratio, x_name, y_name, coord, x_zmin, x_zmax, y_zmin, y_zmax,
    kde_cent, frame_kde_cent, clust_rad, kp_flag, KP_Bys_rc, KP_Bys_rt,
        KP_Bys_ecc, KP_Bys_theta):
    """
    Coordinates 2D KDE zoom.
    """
    ax = plt.subplot(gs[2:4, 2:4])

    plt.xlim(x_zmin, x_zmax)
    plt.ylim(y_zmin, y_zmax)
    plt.xlabel('{} ({})'.format(x_name, coord))
    plt.ylabel('{} ({})'.format(y_name, coord))

    # Radius
    circle = plt.Circle(
        (kde_cent[0], kde_cent[1]), clust_rad, color='r', fill=False)
    ax.add_artist(circle)

    # Core and tidal radii (using mode values)
    if kp_flag:
        # Plot tidal radius.
        rt_mode, ecc_mode, theta_mode = KP_Bys_rt[4], KP_Bys_ecc[4],\
            KP_Bys_theta[4]
        b = rt_mode * np.sqrt(1. - ecc_mode**2)
        ellipse = mpatches.Ellipse(
            xy=kde_cent, width=2. * rt_mode, height=2. * b,
            angle=np.rad2deg(theta_mode), facecolor='None', edgecolor='g',
            linewidth=1.5, transform=ax.transData)
        fig.gca().add_artist(ellipse)
        # Plot core radius.
        rc_mode = KP_Bys_rc[4]
        b = rc_mode * np.sqrt(1. - ecc_mode**2)
        ellipse = mpatches.Ellipse(
            xy=kde_cent, width=2. * rc_mode, height=2. * b,
            angle=np.rad2deg(theta_mode), facecolor='None', edgecolor='g',
            ls='dashed', linewidth=1., transform=ax.transData)
        fig.gca().add_artist(ellipse)

    ext_range, x_grid, y_grid, k_pos = frame_kde_cent
    kde = np.reshape(k_pos.T, x_grid.shape)
    plt.imshow(
        np.rot90(kde), cmap=plt.get_cmap('RdYlBu_r'), extent=ext_range)
    plt.contour(x_grid, y_grid, kde, colors='#551a8b', linewidths=0.5)
    # If RA is used, invert axis.
    if coord == 'deg':
        ax.invert_xaxis()
    ax.set_aspect(aspect=asp_ratio)


def pl_mag_membs(gs, plot_style, y_ax, membvsmag):
    """
    """
    ax = plt.subplot(gs[2:4, 4:6])
    if plot_style == 'asteca':
        ax.grid()
    ax.set_title(r"$N_{{memb}}$ vs magnitude cut (phot incomp)")
    plt.xlabel('$' + y_ax + '$')
    plt.ylabel(r'$N_{memb}$')
    plt.bar(*membvsmag, zorder=5)


def pl_cl_fl_regions(
    gs, fig, plot_style, x_name, y_name, coord, x_min, x_max, y_min, y_max,
    asp_ratio, kde_cent, clust_rad, field_regions_i, field_regions_rjct_i,
        cl_region_i, cl_region_rjct_i, flag_no_fl_regs_i):
    """
    Cluster and field regions defined.
    """
    ax = plt.subplot(gs[4:6, 0:2])

    ax.set_aspect(aspect=asp_ratio)
    # Set plot limits
    # plt.xlim(x_min, x_max)
    # plt.ylim(y_min, y_max)
    # If RA is used, invert axis.
    if coord == 'deg':
        ax.invert_xaxis()
    plt.xlabel('{} ({})'.format(x_name, coord))
    plt.ylabel('{} ({})'.format(y_name, coord))
    if plot_style == 'asteca':
        ax.grid(which='both')
    # Radius
    circle = plt.Circle((kde_cent[0], kde_cent[1]), clust_rad,
                        color='k', fill=False)
    fig.gca().add_artist(circle)

    # Plot cluster region.
    if len(cl_region_rjct_i) > 0:
        plt.scatter(
            list(zip(*cl_region_rjct_i))[1], list(zip(*cl_region_rjct_i))[2],
            marker='o', c='red', s=8, edgecolors='w', lw=.2)
    plt.scatter(list(zip(*cl_region_i))[1], list(zip(*cl_region_i))[2],
                marker='o', c='red', s=8, edgecolors='w', lw=.2)

    N_flrg = 0
    if not flag_no_fl_regs_i:
        col0 = cycle(['DimGray', 'ForestGreen', 'maroon', 'RoyalBlue'])
        col1 = cycle(['DimGray', 'ForestGreen', 'maroon', 'RoyalBlue'])
        # Stars inside the field regions with accepted errors.
        for i, reg in enumerate(field_regions_i):
            fl_reg = list(zip(*reg))
            N_flrg += len(fl_reg[0])
            plt.scatter(fl_reg[1], fl_reg[2], marker='o',
                        c=next(col0), s=8, edgecolors='w', lw=.2)
        # Stars inside the field regions with rejected errors.
        for i, reg in enumerate(field_regions_rjct_i):
            if reg:
                fl_reg = list(zip(*reg))
                N_flrg += len(fl_reg[0])
                plt.scatter(fl_reg[1], fl_reg[2], marker='o',
                            c=next(col1), s=8, edgecolors='w', lw=.2)

    ax.set_title(r"$N_{{stars}}$={} (phot incomp); $N_{{fregs}}$={}".format(
        len(cl_region_i) + len(cl_region_rjct_i) + N_flrg,
        len(field_regions_i)))


def plot(N, *args):
    """
    Handle each plot separately.
    """

    plt_map = {
        0: [pl_rad_find, 'Radius estimation'],
        1: [pl_rad_dens, 'radial density function'],
        2: [pl_zoom_frame, 'zoomed frame'],
        3: [pl_dens_map, 'density map'],
        4: [pl_mag_membs, 'estimated members vs magnitude cut'],
        5: [pl_cl_fl_regions, 'cluster and field regions defined']
    }

    fxn = plt_map.get(N, None)[0]
    if fxn is None:
        raise ValueError("  ERROR: there is no plot {}.".format(N))

    try:
        fxn(*args)
    except Exception:
        print("  WARNING: error when plotting {}".format(plt_map.get(N)[1]))
        import traceback
        print(traceback.format_exc())
