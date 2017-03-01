
from ..synth_clust import synth_cl_plot


def main(clp, npd, er_params, bf_flag, fundam_params, bin_mr, filters,
         colors, theor_tracks, R_V, **kwargs):
    '''
    Create output data file with stars in the best fit synthetic cluster found
    by the 'Best Fit' function.
    '''
    # Check if function should run.
    if bf_flag:

        e_max = er_params[1]
        shift_isoch, synth_clst = synth_cl_plot.main(
            e_max, bin_mr, fundam_params, theor_tracks,
            clp['isoch_fit_params'], clp['err_lst'], clp['completeness'],
            clp['st_dist_mass'], R_V, clp['ext_coefs'], clp['N_fc'])

        # If cluster is not empty.
        if synth_clst:
            # Prepare data.
            mags_cols, e_mags_cols = zip(*synth_clst[0][0]),\
                zip(*synth_clst[0][1])
            binar_idx = synth_clst[1]
            extra_pars = zip(*synth_clst[2])
            # Prepare header.
            hdr = ['#ID           ']
            hdr += [f[1] + '   ' for f in filters]
            hdr += ['(' + c[1].replace(',', '-') + ')   ' for c in colors]
            hdr += ['e_' + f[1] + '   ' for f in filters]
            hdr += ['e_(' + c[1].replace(',', '-') + ')   ' for c in colors]
            hdr = ''.join(hdr) +\
                'M_ini   M_act  logL/Lo  logTe  logG  mbol\n'
            # Save best fit synthetic cluster found to file.
            with open(npd['synth_file_out'], "w") as f_out:
                f_out.write(hdr)
                for i, st in enumerate(mags_cols):
                    if i in binar_idx:
                        ID = '2' + str(i)
                    else:
                        ID = '1' + str(i)
                    f_out.write("{:<8}".format(ID))
                    for _ in st:
                        f_out.write("{:<8.4f}".format(_))
                    for _ in e_mags_cols[i]:
                        f_out.write("{:<8.4f}".format(_))
                    f_out.write("{:<8.4f} {:<8.4f} {:<8.4f} {:<8.4f}"
                                " {:<8.4f} {:<8.4f}\n".format(*extra_pars[i]))

            print('Best fit synthetic cluster saved to file.')
            # Save for plotting.
            clp['synth_clst'], clp['shift_isoch'] = synth_clst, shift_isoch

        else:
            clp['synth_clst'], clp['shift_isoch'] = [], []
            print("  ERROR: empty synthetic cluster could not be saved\n"
                  "  to file.")

    return clp
