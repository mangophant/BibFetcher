# generate a test json file automatically

import os
import json
import time
import random

import dblp
import venue


def load_pub(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            old_pubs = json.load(f)
    else:
        old_pubs = {}
    return old_pubs


def append_pub(old_pubs, new_pubs, file_path):
    pubs = {}
    pubs.update(old_pubs)
    pubs.update(new_pubs)
    with open(file_path, 'w') as f:
        json.dump(pubs, f, indent=4, sort_keys=True)
    

json_file = 'ref.json'
missing_venues = []
for pubtype in venue.PubType:
    venue_names = venue.venue_dict[pubtype].keys()
    print('*' * 20 + str(pubtype) + '*' * 20)
    for i, venue_name in enumerate(venue_names):
        new_pubs = {}
        old_pubs = load_pub(json_file)
        for year in range(2020, 2024):
            index = f'{venue_name}_{year}'
            print(f'[{i+1:3d}/{len(venue_names):3d}] {index}')
            existing_venues = list(filter(lambda k: index in k, old_pubs.keys()))
            if len(existing_venues) >= 3:
                continue
            titles, msg = dblp.search_publication_by_venue(venue_name, year, pubtype)
            if titles is not None and len(titles) > 0:
                for title in titles[:3-len(existing_venues)]:
                    new_pubs[f'{index}_{title.split(" ")[0].lower()}'] = title
            else:
                missing_venues.append(index)
                print('[ERR] ' + msg)
            # time.sleep(random.random())
        append_pub(old_pubs, new_pubs, json_file)
print('*' * 20 + 'missing entries' + '*' * 20)
print(missing_venues)