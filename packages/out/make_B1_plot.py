
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from os.path import join
from . import mp_errors
from . import add_version_plot
from . import prep_plots


def main(
        npd, cld_c, pd, em_float, err_lst, cl_region_c, cl_region_rjct_c,
        stars_out_c, stars_out_rjct_c, col_0_comb, mag_0_comb, **kwargs):
    '''
    Make B1 block plots.
    '''
    if 'B1' in pd['flag_make_plot']:
        fig = plt.figure(figsize=(30, 25))
        gs = gridspec.GridSpec(7, 12)
        add_version_plot.main(y_fix=1.)

        # Obtain plotting parameters and data.
        x_ax0, y_ax = prep_plots.ax_names(
            pd['colors'][0], pd['filters'][0], 'mag')
        x_max_cmd0, x_min_cmd0, y_min_cmd0, y_max_cmd0 =\
            prep_plots.diag_limits('mag', col_0_comb, mag_0_comb)
        # For the error curve 'x_min_cmd' is not used
        err_bar_all = prep_plots.error_bars(
            cld_c['mags'][0], np.nan, err_lst, 'all')

        x_min, x_max, y_min, y_max = prep_plots.frame_max_min(
            cld_c['x'], cld_c['y'])
        coord, x_name, y_name = prep_plots.coord_syst(pd['coords'])

        # Photometric analysis plots.
        arglist = [
            # pl_phot_err: Photometric error rejection.
            [gs, pd['colors'], pd['filters'], pd['id_kinem'], cld_c['mags'],
             em_float, cl_region_c, cl_region_rjct_c, stars_out_c,
             stars_out_rjct_c, err_bar_all]
        ]
        for n, args in enumerate(arglist):
            mp_errors.plot(n, *args)

        plt.suptitle(
            r"$N_{{accpt}}={}$ , $N_{{rjct}}={}$ (compl frame)".format(
                len(cl_region_c) + len(stars_out_c),
                len(stars_out_rjct_c) + len(cl_region_rjct_c)),
            fontsize=12, x=.265, y=1.005)

        # Generate output file.
        fig.tight_layout()
        plt.savefig(
            join(npd['output_subdir'], str(npd['clust_name']) +
                 '_B1.' + pd['plot_frmt']), dpi=pd['plot_dpi'],
            bbox_inches='tight')
        # Close to release memory.
        plt.clf()
        plt.close("all")

        print("<<Plots for B1 block created>>")
    else:
        print("<<Skip B1 block plot>>")