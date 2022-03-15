import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pytz
from scipy.optimize import curve_fit
from matplotlib.transforms import Bbox

DEADLINE = 14    # Deadline is 2 pm Eastern
EASTERN = pytz.timezone('US/Eastern')
ANNOUNCE_DAY = { # When is the paper announced if submitted before/after the deadline?
                 # Submitted: Announced
                    'Mon': ['Mon', 'Tue'],
                    'Tue': ['Tue', 'Wed'],
                    'Wed': ['Wed', 'Thu'],
                    'Thu': ['Thu', 'Sun'],
                    'Fri': ['Sun', 'Mon'],
                    'Sat': ['Mon', 'Mon'],
                    'Sun': ['Mon', 'Mon']
                }

#####
# Data munging
#####

def load_and_process_data(which):
    """
    Combine data from Kaggle with number of citations, process and add new features.
    
    Drops papers without citation info. Converts citation counts to int. Calculates
    citation boost as ratio of the number of citations and the average number of
    citations. Converts the submission datetime to Eastern timezone. Add columns:
    * 'hour'/'minute'/'second' - sumission time
    * 'after_deadline' - is submitted after 2 pm?
    * 'announced_on' - which day of the week was paper announced?
    * 'minute_bin' - submission minute rounded down, one of '00', '10', '20', ... '50'
    * 'time' - submission time, rounded down to ten minutes, in the format HH:MM
    * 'previous_deadline' - on which day did the submission round open?
    
    Returns a pandas dataframe.
    """
    dat = pd.read_csv('data/' + which + '.csv', parse_dates = ['submitted_on'], 
                        date_parser=lambda x: pd.to_datetime(x, utc=True),)
    citation_counts = pd.read_csv('data/' + which + '_citation_counts.csv')

    assert(all(dat['id'] == citation_counts['id']))
    assert(len(dat) == len(citation_counts))

    dat['citation_counts'] = citation_counts['citation_counts']

    dat = dat[dat['citation_counts'] != 'None']

    dat['citation_counts'] = dat['citation_counts'].astype(int)

    print(f"Average number of citations for {which} is {dat['citation_counts'].mean():.2f}")

    dat['citation_boost'] = 100*(dat['citation_counts']/dat['citation_counts'].mean() - 1)

    dat['submitted_on'] = dat['submitted_on'].dt.tz_convert(EASTERN)

    dat['hour'] = dat['submitted_on'].dt.hour
    dat['minute'] = dat['submitted_on'].dt.minute
    dat['second'] = dat['submitted_on'].dt.second

    dat['after_deadline'] = dat['hour'] >= DEADLINE

    dat['announced_on'] = dat.apply(lambda x: ANNOUNCE_DAY[x.weekday][x.after_deadline], axis = 1)

    dat['minute_bin'] = 10*(dat['minute'] // 10)
    dat['minute_bin'] = dat['minute_bin'].astype(str)
    dat.loc[dat['minute_bin'] == '0', 'minute_bin'] = '00'

    dat['time'] = dat['hour'].astype(str) + ':' + dat['minute_bin']

    # On which date did the submissions open?
    dat['previous_deadline'] = dat['submitted_on'].dt.date
    dat.loc[dat['after_deadline'] == 0, 'previous_deadline'] -= pd.Timedelta(1, unit='D')
    dat.loc[(dat['after_deadline'] == 1) & (dat['weekday'] == 'Sat'), 'previous_deadline'] -= pd.Timedelta(1, unit='D')
    dat.loc[(dat['after_deadline'] == 0) & (dat['weekday'] == 'Sun'), 'previous_deadline'] -= pd.Timedelta(1, unit='D')
    dat.loc[(dat['after_deadline'] == 1) & (dat['weekday'] == 'Sun'), 'previous_deadline'] -= pd.Timedelta(2, unit='D')
    dat.loc[(dat['after_deadline'] == 0) & (dat['weekday'] == 'Mon'), 'previous_deadline'] -= pd.Timedelta(2, unit='D')

    return dat

#####
# Routines related to styling and saving plots
#####

def style_plot(axs):
    """
    Apply some styling to the plot to make them look nice
    """
    axs[0].spines['right'].set_visible(False) # Hide the bounding box
    axs[0].spines['top'].set_visible(False)
    axs[0].spines['left'].set_visible(False)
    axs[1].spines['right'].set_visible(False)
    axs[1].spines['top'].set_visible(False)
    axs[1].spines['left'].set_visible(False)

    axs[0].tick_params(left=False, bottom=False) # Hide the ticks
    axs[1].tick_params(left=False, bottom=False)

    plt.subplots_adjust(                        # Space between plots
                        wspace=0.4,
                        hspace=0.4)

def full_extent(ax, pad=0.0):
    """Get the full extent of an axes, including axes labels, tick labels, and
    titles."""
    # For text objects, we need to draw the figure first, otherwise the extents
    # are undefined.
    ax.figure.canvas.draw()
    items = ax.get_xticklabels() + ax.get_yticklabels()
    items += [ax, ax.title, ax.xaxis.label, ax.yaxis.label]
    bbox = Bbox.union([item.get_window_extent() for item in items])

    return bbox.expanded(1.0 + pad, 1.0 + pad)

def save_plots(f, axs, name):
    """
    Save both subplots combined, as well as separately
    """
    plt.savefig(f'img/{name}.png', bbox_inches = 'tight')

    extent = full_extent(axs[0]).transformed(f.dpi_scale_trans.inverted())
    plt.savefig(f'img/{name}_A.png', bbox_inches=extent.expanded(1.1,1.1))

    extent = full_extent(axs[1]).transformed(f.dpi_scale_trans.inverted())
    plt.savefig(f'img/{name}_B.png', bbox_inches=extent.expanded(1.1,1.1))
