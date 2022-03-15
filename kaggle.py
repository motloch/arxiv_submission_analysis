"""
Code from https://www.kaggle.com/motloch/arxiv-analysis used to download information about
arXiv papers - ID, submission time, number of authors, submitter. 

Uses the official Kaggle arXiv Dataset (https://www.kaggle.com/Cornell-University/arxiv).
"""

import numpy as np
import pandas as pd
import json

months_dict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun' : '06',
              'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}

# Data processing based on
# https://www.kaggle.com/srishti280992/prep-data-for-coauthorship-analysis
def get_clean_authors(authors):
    """
    Merge first and last name of the authors
    """
    r = []
    for a in authors:
        r.append(" ".join(a).strip())
    return r

def get_data_and_save(category, pick_year):
    """
    Saves information about arxiv articles from the given category and year.
    """
    articles = []
    with open("../input/arxiv/arxiv-metadata-oai-snapshot.json", "r") as f:
        for l in f:
            d = json.loads(l)
            # Only the primary classification. Note that we can have astro-ph.CO and similar, so we strip the ending.
            if category in d['categories'].split(' ')[0][:len(category)]:
                if pick_year in d['versions'][0]['created']:
                    num_authors = len(get_clean_authors(d['authors_parsed']))

                    created = d['versions'][0]['created']
                    splitted = created.split(' ')
                    weekday = splitted[0][:-1]
                    day = int(splitted[1])
                    month = months_dict[splitted[2]]
                    year = splitted[3]
                    time = splitted[4]
                    datetime_string = f'{year}-{month}-{day:02} {time}'

                    articles.append((d['id'], d['submitter'], weekday, np.datetime64(datetime_string), num_authors))

    dat = pd.DataFrame(articles)
    dat.columns = ['id', 'submitter', 'weekday', 'submitted_on', 'num_authors']

    dat.to_csv(pick_year + '_' + category + '.csv', index = False)

#####
# Extract the data about papers
#####

get_data_and_save('hep-th', '2015')
get_data_and_save('hep-th', '2016')
get_data_and_save('hep-th', '2017')
get_data_and_save('hep-th', '2018')
get_data_and_save('hep-th', '2019')
get_data_and_save('hep-th', '2020')
