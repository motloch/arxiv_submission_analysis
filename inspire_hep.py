#!/usr/bin/env python3

"""
Given a list of arxiv IDs (e.g. 2101.12345), output a file with number of citations of
these papers obtained from the inspire hep database (https://inspirehep.net) using their
API
"""

import urllib.request, json
import pandas as pd
import sys

if len(sys.argv) == 3:
    YEAR = sys.argv[1]
    CATEGORY = sys.argv[2]
else:
    print('Usage: python inspire_hep.py YEAR CATEGORY')
    print('Usage: python inspire_hep.py 2021 hep-th')
    exit()

#####
# Function that scrapes the number of citation from Inspire Hep
#####

URL_TEMPLATE = 'https://inspirehep.net/api/literature?fields=citation_count&q=arxiv:' 

def get_citation_count(arxiv_number):
    """
    Given arxiv number, scrape inspire hep an get the number of citations of the given
    paper
    """
    url = URL_TEMPLATE + str(arxiv_number)
    api_response = json.loads(urllib.request.urlopen(url).read())
    not_found = len(api_response['hits']['hits']) == 0
    if not_found:
        citation_count = None
    else:
        citation_count = api_response['hits']['hits'][0]['metadata']['citation_count']
    return citation_count

#####
# File with arxiv numbers we are interested in
#####
    
arxiv_numbers = pd.read_csv('data/' + YEAR + '_' + CATEGORY + '.csv', usecols = ['id'], dtype = str)['id'].values
print(f'Loaded {len(arxiv_numbers)} arxiv IDs.')

#####
# Process them and save results
#####

out = open('data/' + YEAR + '_' + CATEGORY + '_citation_counts.csv', 'w')
out.write('id,citation_counts\n')
for i, arxiv_number in enumerate(arxiv_numbers):
    if i % 1000 == 0:
        print(f'Processing {i}-th record')
    citation_count = get_citation_count(arxiv_number)
    out.write(arxiv_number + ',' + str(citation_count) + '\n')

out.close()
