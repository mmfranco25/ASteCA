
import numpy as np
from scipy.spatial.distance import cdist


def main(clp, coords, project, **kwargs):
    """
    """
    PM_flag = False
    pmMP, pmRA_DE, e_pmRA_DE, pmDE, e_pmDE, mmag_pm, PM_cl_x, PM_cl_y,\
        PM_cl_z, PM_fl_x, PM_fl_y, pmDE_fl, e_pmDE_fl, pmRA_fl_DE,\
        e_pmRA_fl_DE, pm_dist_max = [[] for _ in range(16)]
    PM_fl_z = np.array([])
    PMs_cl_cx, PMs_cl_cy, PMs_fl_cx, PMs_fl_cy = [np.nan] * 4

    # Extract RA PMs data.
    pmRA = np.array(list(zip(*list(zip(*clp['cl_reg_fit']))[7]))[1])
    # Array with no nan values
    pmRA_clrg = pmRA[~np.isnan(pmRA)]

    # Check that PMs were defined within the cluster region.
    if pmRA_clrg.any():
        PM_flag = True

        # Cluster region data.
        pmMP, pmRA, e_pmRA, pmDE, e_pmDE =\
            np.array(list(zip(*clp['cl_reg_fit']))[9]),\
            np.array(list(zip(*list(zip(*clp['cl_reg_fit']))[7]))[1]),\
            np.array(list(zip(*list(zip(*clp['cl_reg_fit']))[8]))[1]),\
            np.array(list(zip(*list(zip(*clp['cl_reg_fit']))[7]))[2]),\
            np.array(list(zip(*list(zip(*clp['cl_reg_fit']))[8]))[2])
        mmag_pm = np.array(list(zip(*list(zip(*clp['cl_reg_fit']))[3]))[0])

        # Apply cos(delta) correction to pmRA if possible.
        if coords == 'deg':
            if project:
                DE_pm = np.array(list(zip(*clp['cl_reg_fit']))[2]) +\
                    clp['y_offset']
            else:
                DE_pm = np.array(list(zip(*clp['cl_reg_fit']))[2])
        else:
            print("  WARNING: can not apply cos(dec) factor to pmRA.")
            DE_pm = np.zeros(pmRA.size)

        # Remove nan values from cluster region
        msk = ~np.isnan(pmRA) & ~np.isnan(e_pmRA) & ~np.isnan(pmDE) &\
            ~np.isnan(e_pmDE)
        pmMP, pmRA, e_pmRA, pmDE, e_pmDE, DE_pm, mmag_pm = pmMP[msk],\
            pmRA[msk], e_pmRA[msk], pmDE[msk], e_pmDE[msk], DE_pm[msk],\
            mmag_pm[msk]

        pmRA_DE = pmRA * np.cos(np.deg2rad(DE_pm))
        # Propagate error in RA*cos(delta)
        e_pmRA_DE = np.sqrt(
            (e_pmRA * pmRA * np.sin(np.deg2rad(DE_pm)))**2 +
            (e_pmDE * np.cos(np.deg2rad(DE_pm)))**2)

        # Error weighted 2D KDE for cluster region
        PM_cl_x, PM_cl_y, PM_cl_z = kde_2d(pmRA_DE, e_pmRA_DE, pmDE, e_pmDE)
        # Max value
        PMs_cl_cx, PMs_cl_cy = np.unravel_index(
            PM_cl_z.argmax(), PM_cl_z.shape)

        # PM distances to the KDE's center.
        pm_dist_max = cdist(
            np.array([
                [PM_cl_x[PMs_cl_cx][PMs_cl_cy],
                 PM_cl_y[PMs_cl_cx][PMs_cl_cy]]]), np.array([pmRA_DE, pmDE]).T)

        # Process field regions
        if not clp['flag_no_fl_regs_i']:
            pmRA_fl, e_pmRA_fl, DE_fl_pm = [], [], []
            # Field region(s) data.
            for fl_rg in clp['field_regions_i']:
                pmRA_fl += list(zip(*list(zip(*fl_rg))[7]))[1]
                e_pmRA_fl += list(zip(*list(zip(*fl_rg))[8]))[1]
                pmDE_fl += list(zip(*list(zip(*fl_rg))[7]))[2]
                e_pmDE_fl += list(zip(*list(zip(*fl_rg))[8]))[2]
                DE_fl_pm += list(list(zip(*fl_rg)))[2]

            pmRA_fl, e_pmRA_fl, pmDE_fl, e_pmDE_fl, DE_fl_pm = [
                np.asarray(_) for _ in (
                    pmRA_fl, e_pmRA_fl, pmDE_fl, e_pmDE_fl, DE_fl_pm)]

            # Remove nan values from field region(s)
            msk = ~np.isnan(pmRA_fl) & ~np.isnan(e_pmRA_fl) &\
                ~np.isnan(pmDE_fl) & ~np.isnan(e_pmDE_fl)
            pmRA_fl, e_pmRA_fl, pmDE_fl, e_pmDE_fl, DE_fl_pm = \
                pmRA_fl[msk], e_pmRA_fl[msk], pmDE_fl[msk], e_pmDE_fl[msk],\
                DE_fl_pm[msk]

            pmRA_fl_DE = pmRA_fl * np.cos(np.deg2rad(DE_fl_pm))
            # Propagate error in RA*cos(delta)
            e_pmRA_fl_DE = np.sqrt(
                (e_pmRA_fl * pmRA_fl * np.sin(np.deg2rad(DE_fl_pm)))**2 +
                (e_pmDE_fl * np.cos(np.deg2rad(DE_fl_pm)))**2)

            PM_fl_x, PM_fl_y, PM_fl_z = kde_2d(
                pmRA_fl_DE, e_pmRA_fl_DE, pmDE_fl, e_pmDE_fl)
            # Max value
            PMs_fl_cx, PMs_fl_cy = np.unravel_index(
                PM_fl_z.argmax(), PM_fl_z.shape)

    clp.update({
        'PM_flag': PM_flag, 'pmMP': pmMP, 'pmRA_DE': pmRA_DE,
        'e_pmRA_DE': e_pmRA_DE, 'pmDE': pmDE, 'e_pmDE': e_pmDE,
        'mmag_pm': mmag_pm, 'PM_cl_x': PM_cl_x, 'PM_cl_y': PM_cl_y,
        'PM_cl_z': PM_cl_z, 'PMs_cl_cx': PMs_cl_cx, 'PMs_cl_cy': PMs_cl_cy,
        'pmRA_fl_DE': pmRA_fl_DE, 'e_pmRA_fl_DE': e_pmRA_fl_DE,
        'pmDE_fl': pmDE_fl, 'e_pmDE_fl': e_pmDE_fl,
        'PM_fl_x': PM_fl_x, 'PM_fl_y': PM_fl_y, 'PM_fl_z': PM_fl_z,
        'PMs_fl_cx': PMs_fl_cx, 'PMs_fl_cy': PMs_fl_cy,
        'pm_dist_max': pm_dist_max})
    return clp


def kde_2d(xarr, xsigma, yarr, ysigma, grid_dens=50):
    '''
    Take an array of x,y data with their errors, create a grid of points in x,y
    and return the 2D KDE density map.
    '''

    # Replace 0 error with very LARGE value.
    np.place(xsigma, xsigma <= 0., 1000.)
    np.place(ysigma, ysigma <= 0., 1000.)

    # Grid density (number of points).
    xmean, xstd = np.nanmedian(xarr), np.nanstd(xarr)
    ymean, ystd = np.nanmedian(yarr), np.nanstd(yarr)
    xmax, xmin = xmean + 3. * xstd, xmean - 3. * xstd
    ymax, ymin = ymean + 3. * ystd, ymean - 3. * ystd
    gd_c = complex(0, grid_dens)
    # Define grid of points in x,y where the KDE will be evaluated.
    ext = [xmin, xmax, ymin, ymax]
    x, y = np.mgrid[ext[0]:ext[1]:gd_c, ext[2]:ext[3]:gd_c]
    pos = np.vstack([x.ravel(), y.ravel()])
    values = np.vstack([xarr, yarr])

    # Scipy's norm factor
    # https://github.com/scipy/scipy/blob/v1.1.0/scipy/stats/kde.py
    d, n = values.shape
    data_covariance = np.cov(values)
    data_inv_cov = np.linalg.inv(data_covariance)
    scotts_factor = np.power(n, -1. / (d + 4))
    inv_cov = data_inv_cov / scotts_factor**2
    covariance = data_covariance * scotts_factor**2
    norm_factor = np.sqrt(np.linalg.det(2 * np.pi * covariance)) * n

    # Evaluate KDE in x,y grid.
    m = grid_dens**2
    vals = np.zeros((m,), dtype=np.float)
    if m >= n:
        # print("loop over data")
        e_values = np.vstack([xsigma, ysigma]).T
        for i, p in enumerate(values.T):
            valxy = (
                inv_cov[0][0] * ((p[0] - pos[0]) / e_values[i][0])**2 +
                inv_cov[1][1] * ((p[1] - pos[1]) / e_values[i][1])**2) /\
                (e_values[i][0] * e_values[i][1])
            vals += np.exp(-.5 * valxy)
        result = np.array(vals)
    else:
        # print("loop over points")
        for i, p in enumerate(zip(*pos)):
            valxy = (
                inv_cov[0][0] * ((p[0] - xarr) / xsigma)**2 +
                inv_cov[1][1] * ((p[1] - yarr) / ysigma)**2) /\
                (xsigma * ysigma)
            vals[i] = np.sum(np.exp(-.5 * valxy))
    result = vals / norm_factor

    # Re-shape values for plotting.
    z = np.reshape(result.T, x.shape)

    return x, y, z
