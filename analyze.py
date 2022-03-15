import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.optimize import curve_fit
from utils import DEADLINE, load_and_process_data, style_plot, save_plots

weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
announce_days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu']

#####
# Load the data
#####

dat_2015 = load_and_process_data('2015_hep-th')
dat_2016 = load_and_process_data('2016_hep-th')
dat_2017 = load_and_process_data('2017_hep-th')
dat_2018 = load_and_process_data('2018_hep-th')
dat_2019 = load_and_process_data('2019_hep-th')
dat_2020 = load_and_process_data('2020_hep-th')

dat_list = (dat_2015, dat_2016, dat_2017, dat_2018, dat_2019, dat_2020)

dat_all = pd.concat(dat_list)
dat_recent = pd.concat(dat_list[2:]) # 2015, 2016 had a different submission deadline

#####
# Average number of citations for each year
#####

years = np.arange(2015, 2021)
avg_cit_count = [x['citation_counts'].mean() for x in dat_list]

# Fit an exponential function timestamp -> expected number of citations
def fit_func(x, amp, c, shift):
    return amp*(1 - np.exp(c * (x/1e9 - shift)))
x = np.array([datetime.strptime(str(year) + '-06-30', '%Y-%m-%d').timestamp() for year in years])
fit_pars = curve_fit(fit_func, x, avg_cit_count, p0 = (29.6, 10, 1.62))[0]

# Output a plot showing how good the fit is
plt.scatter(x, avg_cit_count)
plt.plot(x, fit_func(x, *fit_pars))
plt.xlabel('timestamp')
plt.ylabel('Average number of citations')
plt.savefig('img/arxiv_citation_fit.png', bbox_inches = 'tight')

# If we want to calculate citation boost more accurately, we now can. Does not seem to
# change conclusions so we will ignore it.
dat_recent['timestamp'] = [x.timestamp() for x in dat_recent['submitted_on']]
dat_recent['citation_boost_accurate'] = 100*(dat_recent['citation_counts'] / fit_func(dat_recent['timestamp'], *fit_pars)-1)

##### Summary statistics

years = range(2015, 2021)
counts = [len(x) for x in dat_list]
avg_cit_count = [x['citation_counts'].mean() for x in dat_list]

f, axs = plt.subplots(1,2, figsize=(12,3),dpi=300)

axs[0].bar(years, counts,        color = 'goldenrod')
axs[1].bar(years, avg_cit_count, color = 'goldenrod')

axs[0].set_title('Number of submissions',       fontfamily = 'Arial Black', pad = 20)
axs[1].set_title('Average number of citations', fontfamily = 'Arial Black', pad = 20)
axs[0].set_xlabel('Submission year')
axs[1].set_xlabel('Submission year')

style_plot(axs)

save_plots(f, axs, 'arxiv_summary')

##### Day of submission

counts = dat_all.groupby('weekday')['citation_boost'].count()
counts = [counts[wd] for wd in weekdays] # Order Mon-Sun

means = dat_all.groupby('weekday')['citation_boost'].mean()
avg_cit_count = [means[wd] for wd in weekdays]

f, axs = plt.subplots(1,2, figsize=(12,3),dpi=300)

axs[0].bar(range(7), counts,        color = 'goldenrod')
axs[1].bar(range(7), avg_cit_count, color = 'goldenrod')
axs[1].axhline(0, color = 'black', lw = 0.6)

axs[0].set_title('Number of submissions', fontfamily = 'Arial Black', pad = 20)
axs[1].set_title('Excess citations',      fontfamily = 'Arial Black', pad = 20)
axs[0].set_xlabel('Day of submission')
axs[1].set_xlabel('Day of submission')

axs[0].set_xticks(range(7), weekdays)
axs[1].set_xticks(range(7), weekdays)
axs[1].set_yticks([-30, -20, -10, 0, 10], ['-30%', '-20%', '-10%', '0%', '10%'])

style_plot(axs)
save_plots(f, axs, 'arxiv_weekdays')

##### Hour of submission

avg_cit_count = dat_recent.groupby('hour')['citation_boost'].mean()
counts = dat_recent.groupby('hour')['citation_boost'].count()

f, axs = plt.subplots(1,2, figsize=(12,3),dpi=300)

axs[0].bar(range(24), counts,        color = 'goldenrod')
axs[1].bar(range(24), avg_cit_count, color = 'goldenrod')
axs[1].axhline(0, color = 'black', lw = 0.6)

axs[0].set_title('Number of submissions', fontfamily = 'Arial Black', pad = 20)
axs[1].set_title('Excess citations',      fontfamily = 'Arial Black', pad = 20)
axs[0].set_xlabel('Time of submission')
axs[1].set_xlabel('Time of submission')

axs[0].axvline(DEADLINE - 0.5, color = 'k', ls = '--')
axs[1].axvline(DEADLINE - 0.5, color = 'k', ls = '--')
ymax = axs[0].get_ylim()[1]
axs[0].text(DEADLINE - 5.3, 0.97*ymax, 'Deadline', fontfamily = 'Arial Black')

axs[0].set_xticks([0,4,8,12,16,20,24], ['midnight', '4 am', '8 am', 'noon', '4 pm', '8 pm', 'EST/EDT'])
axs[1].set_xticks([0,4,8,12,16,20,24], ['midnight', '4 am', '8 am', 'noon', '4 pm', '8 pm', 'EST/EDT'])
axs[1].set_yticks([-40,-20,0,20,40], ['-40%', '-20%', '0%', '20%', '40%'])

style_plot(axs)

save_plots(f, axs, 'arxiv_hours')

##### Announcement day

counts = dat_recent.groupby('announced_on')['citation_boost'].count()
counts = [counts[ad] for ad in announce_days] # Order Sun - Thu

means = dat_recent.groupby('announced_on')['citation_boost'].mean()
avg_cit_count = [means[ad] for ad in announce_days]

f, axs = plt.subplots(1,2, figsize=(12,3),dpi=300)

axs[0].bar(range(5), counts,        color = 'goldenrod')
axs[1].bar(range(5), avg_cit_count, color = 'goldenrod')
axs[1].axhline(0, color = 'black', lw = 0.6)

axs[0].set_title('Number of submissions', fontfamily = 'Arial Black', pad = 20)
axs[1].set_title('Excess citations',      fontfamily = 'Arial Black', pad = 20)
axs[0].set_xlabel('Day of announcement')
axs[1].set_xlabel('Day of announcement')

axs[0].set_xticks(range(5), announce_days)
axs[1].set_xticks(range(5), announce_days)
axs[1].set_yticks([-10, 0, 10], ['-10%', '0%', '10%'])

style_plot(axs)

save_plots(f, axs, 'arxiv_announced_on')

##### Day of submission, before/after deadline

means = dat_recent[dat_recent['after_deadline'] == 0].groupby('weekday')['citation_boost'].mean()
before_avg_cit_count = [means[wd] for wd in weekdays]

counts = dat_recent[dat_recent['after_deadline'] == 0].groupby('weekday')['citation_boost'].count()
before_counts = [counts[wd] for wd in weekdays]

means = dat_recent[dat_recent['after_deadline'] == 1].groupby('weekday')['citation_boost'].mean()
after_avg_cit_count = [means[wd] for wd in weekdays]

counts = dat_recent[dat_recent['after_deadline'] == 1].groupby('weekday')['citation_boost'].count()
after_counts = [counts[wd] for wd in weekdays]

f, axs = plt.subplots(1,2, figsize=(12,3),dpi=300)

axs[0].bar(np.arange(7) - 0.2, before_counts, color = 'goldenrod', width = 0.4, label = 'Before 2 pm')
axs[1].bar(np.arange(7) - 0.2, before_avg_cit_count, color = 'goldenrod', width = 0.4)
axs[0].bar(np.arange(7) + 0.2, after_counts, color = 'cornflowerblue', width = 0.4, label = 'After 2 pm')
axs[1].bar(np.arange(7) + 0.2, after_avg_cit_count, color = 'cornflowerblue', width = 0.4)
axs[1].axhline(0, color = 'black', lw = 0.6)

axs[0].set_title('Number of submissions', fontfamily = 'Arial Black', pad = 20)
axs[1].set_title('Excess citations', fontfamily = 'Arial Black', pad = 20)
axs[0].set_xlabel('Day of submission')
axs[1].set_xlabel('Day of submission')

axs[0].legend()

axs[0].set_xticks(range(7), weekdays)
axs[1].set_xticks(range(7), weekdays)
axs[1].set_yticks([-30,-20,-10, 0, 10,20], ['-30%', '-20%', '-10%', '0%', '10%','20%'])

style_plot(axs)

save_plots(f, axs, 'arxiv_split_weekdays')

##### Time of submission, +- 1 hour only

dat_around_deadline = dat_recent.query('hour >= 13 and hour < 15')
dat_around_deadline = dat_around_deadline.query("weekday not in ('Sat', 'Sun')")
counts = dat_around_deadline.groupby(['time'])['citation_boost'].count()
avg_cit_count = dat_around_deadline.groupby(['time'])['citation_boost'].mean()

f, axs = plt.subplots(1,2, figsize=(12,3),dpi=300)

axs[0].bar(np.arange(12), counts,        color = 'goldenrod')
axs[1].bar(np.arange(12), avg_cit_count, color = 'goldenrod')
axs[1].axhline(0, color = 'black', lw = 0.6)

axs[0].set_title('Number of submissions', fontfamily = 'Arial Black', pad = 20)
axs[1].set_title('Excess citations',      fontfamily = 'Arial Black', pad = 20)
axs[0].set_xlabel('Time of submission')
axs[1].set_xlabel('Time of submission')

axs[0].set_xticks(2*np.arange(6), counts.index[::2])
axs[1].set_xticks(2*np.arange(6), counts.index[::2])
axs[1].set_yticks([0, 20,40,60], ['0%', '20%','40%','60%'])

style_plot(axs)

save_plots(f, axs, 'arxiv_zoom_hours')

##### Position in the listing

# Find papers that had the common previous deadline, rank them by submission time
dat_recent['rank'] = dat_recent.groupby('previous_deadline')['submitted_on'].rank().astype(int)
dat_recent.reset_index()

counts        = dat_recent.groupby(['rank'])['citation_boost'].count() 
avg_cit_count = dat_recent.groupby(['rank'])['citation_boost'].mean()

f, axs = plt.subplots(1,2, figsize=(12,3),dpi=300)

axs[0].bar(range(20), counts[:20],        color = 'goldenrod')
axs[1].bar(range(20), avg_cit_count[:20], color = 'goldenrod')
axs[1].axhline(0, color = 'black', lw = 0.6)

axs[0].set_title('Number of submissions', fontfamily = 'Arial Black', pad = 20)
axs[1].set_title('Excess citations',      fontfamily = 'Arial Black', pad = 20)
axs[0].set_xlabel('Position in the arXiv listing')
axs[1].set_xlabel('Position in the arXiv listing')

style_plot(axs)

axs[0].set_xticks(2*np.arange(10), counts.index[:20:2])
axs[1].set_xticks(2*np.arange(10), counts.index[:20:2])
axs[1].set_yticks([-20, -10, 0, 10,20,30], ['-20%', '-10%', '0%', '10%','20%','30%'])

save_plots(f, axs, 'arxiv_rank')

##### Ranking only for those in the first minute

quick = dat_recent.query('hour == 14 and minute == 0 and weekday not in ("Sat", "Sun")')

counts        = quick.groupby('rank')['citation_boost'].count() 
avg_cit_count = quick.groupby('rank')['citation_boost'].mean()

f, axs = plt.subplots(1,2, figsize=(12,3),dpi=300)

axs[0].bar(range(6), counts[:6],        color = 'goldenrod')
axs[1].bar(range(6), avg_cit_count[:6], color = 'goldenrod')
axs[1].axhline(0, color = 'black', lw = 0.6)

axs[0].set_title('Number of submissions (first minute only)', fontfamily = 'Arial Black', pad = 20)
axs[1].set_title('Excess citations (first minute only)',      fontfamily = 'Arial Black', pad = 20)
axs[0].set_xlabel('Position in the arXiv listing')
axs[1].set_xlabel('Position in the arXiv listing')

style_plot(axs)

axs[0].set_xticks(np.arange(6), counts.index[:6])
axs[1].set_xticks(np.arange(6), counts.index[:6])
axs[1].set_yticks([0, 10,20,30,40,50], ['0%', '10%','20%','30%', '40%', '50%'])

save_plots(f, axs, 'arxiv_rank_for_quick')

##### What if someone is top listing, but not submitted in the first minute?

lucky = dat_recent.query('rank == 1 and (hour != 14 or minute != 0 or weekday in ("Sat", "Sun"))')
print(f'\nThere are {len(lucky)} papers who appeared in the top but were not submitted in the first minute.')
print(f'They on average have {-lucky["citation_boost"].mean():.2f}% less citations.')
