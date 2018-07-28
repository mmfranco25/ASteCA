
import traceback
import numpy as np


def mag_ranges(x, y, mags):
    """
    Separate coordinates of observed stars into four magnitude ranges.
    """
    main_mag = mags[0]
    m0, m4 = min(main_mag), max(main_mag)
    mag_step = (m4 - m0) / 4.
    m1, m2, m3 = m0 + mag_step, m0 + 2. * mag_step, m0 + 3. * mag_step

    # Populate ranges
    r0, r1, r2, r3, r4 = [], [], [], [], []
    for st in zip(*[x, y, main_mag]):
        r0.append(st)
        if st[2] < m1:
            r1.append(st)
        elif m1 <= st[2] < m2:
            r2.append(st)
        elif m2 <= st[2] < m3:
            r3.append(st)
        elif m3 <= st[2]:
            r4.append(st)

    xy_mag_ranges = [
        {'[{:.1f}, {:.1f}]'.format(m0, m4): r0},
        {'[{:.1f}, {:.1f})'.format(m0, m1): r1},
        {'[{:.1f}, {:.1f})'.format(m1, m2): r2},
        {'[{:.1f}, {:.1f})'.format(m2, m3): r3},
        {'[{:.1f}, {:.1f}]'.format(m3, m4): r4}
    ]

    return xy_mag_ranges


def main(clp, x, y, mags, **kwargs):
    """
    Return 2D histograms for the x,y positional data.
    """

    # Separate x,y data into magnitude ranges.
    xy_mag_ranges = mag_ranges(x, y, mags)

    # Use the same bin width for all histograms.
    xmin, xmax = min(x), max(x)
    ymin, ymax = min(y), max(y)
    # Calculate the number of bins used.
    x_rang, y_rang = (xmax - xmin), (ymax - ymin)
    # Bin width to create the 2D histogram.
    bin_width = min(x_rang, y_rang) / 100.
    # Number of bins in x,y given the bin width.
    binsxy = [int(x_rang / bin_width), int(y_rang / bin_width)]

    hist_2d = []
    # Obtain 2D x,y histogram for each magnitude range.
    for xym_rang in xy_mag_ranges:
        xr, yr, dummy = list(zip(*list(xym_rang.values())[0]))

        try:
            # hist_2d is the 2D histogram, *edges store the edges of the bins.
            h2d, xedges, yedges = np.histogram2d(
                xr, yr, range=[[xmin, xmax], [ymin, ymax]], bins=binsxy)
            hist_2d.append(h2d)
        except ValueError:
            print("ERROR: Could not generate the positional 2D histogram.")
            print(traceback.format_exc())

    # Add to cluster's parameters dictionary.
    clp['xy_mag_ranges'], clp['bin_width'], clp['hist_2d'], clp['xedges'],\
        clp['yedges'] = xy_mag_ranges, bin_width, hist_2d, xedges, yedges

    print("Frame's 2D histograms obtained.")

    return clp
