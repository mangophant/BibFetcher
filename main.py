#! /usr/bin/env python3
import os
import time
import math
import json
import random
import argparse
import logging

from bib import BibEntry, info2str
from dblp import search_publication


def run():
    parser = argparse.ArgumentParser(description='Import bibliography entries from  DBLP.')
    parser.add_argument('-i', '--input', metavar='INPUT_JSON_FILE', type=str,
                        default='ref.json', help='File name of input .json file with columns [citekey, title, author<optional>]')
    parser.add_argument('-o','--output', metavar='OUTPUT_BIB_OR_TXT_FILE', type=str,
                        default='ref.bib', help='File name of output .bib or .txt file')
    parser.add_argument('-l', '--logfile', metavar='LOG_FILE', type=str,
                        default='ref.log', help='File name of the logging file')
    parser.add_argument('-t', '--time_sleep', metavar='TIME_SLEEP', type=int,
                        default=1, help='Sleep interval between two queries')
    parser.add_argument('-n', '--num_fetch', metavar='NUM_FETCH', type=int,
                        default=3, help='Maximum number of fetching for each entry')
    parser.add_argument('-k', '--keep_empty_field', action='store_true', help='Output empty field in the bib entry or not')
    args = parser.parse_args()
    
    logging.basicConfig(format='%(asctime)s %(filename)s line:%(lineno)d %(levelname)s %(message)s',
                    handlers=[logging.StreamHandler(), logging.FileHandler(args.logfile, 'a')],
                    datefmt='%H:%M:%S', level=logging.INFO)

    missing_bibs = {}
    with open(args.input, 'r') as f:
        query_dict = json.load(f)
    f = open(args.output, 'w', encoding='utf-8')
    for index, (citekey, query) in enumerate(query_dict.items()):
        prefix = f'Entry: [{index+1:3d}/{len(query_dict):3d}]'
        if citekey == '' or query == '':
            logging.warning(prefix + 'Empty citekey or query')
        else:
            info, count = None, 0
            # Fetch bib with multiple tries
            while count < args.num_fetch:
                time.sleep(random.random() * args.time_sleep)
                count += 1
                candidate_infos, msg = search_publication(query)
                logging.info(f'{prefix} {citekey:20s} Try: ({count:d}/{args.num_fetch:d}) >> {msg}')
                if candidate_infos is not None:
                    print(len(candidate_infos))
                    if len(candidate_infos) == 0:
                        logging.warning('No matched candidate, please check the query infomaiton')
                    elif len(candidate_infos) == 1:
                        info = candidate_infos[0]
                    else:
                        # Deal with multiple matches through page navigation
                        print('>> Multiple entry matched:\n')

                        def print_candidate_page(page, num_pages, interval):
                            start = page * interval
                            end = start + interval
                            print('(0) Keep Empty\n')
                            for i, candicate_info in enumerate(candidate_infos[start:end]):
                                print(f'({i+1}) ' + info2str(candicate_info) + '\n')
                            print(f'(u) Page Up | Page {page+1:2d}/{num_pages:2d} | (d) Page Down\n')
                        
                        cur_page, selected_index, interval = 0, -1, 5
                        num_pages = math.ceil(len(candidate_infos) / interval)
                        print_candidate_page(cur_page, num_pages, interval)
                        while selected_index == -1:
                            command = input('>> Choose candidate or navigate page:').strip()
                            if command == 'u':
                                cur_page = max(cur_page - 1, 0)
                                print_candidate_page(cur_page, num_pages, interval)
                            elif command == 'd':
                                cur_page = min(cur_page + 1, num_pages - 1)
                                print_candidate_page(cur_page, num_pages, interval)
                            elif command.isdigit():
                                selected_index = int(command)
                                if selected_index == 0:
                                    info = None
                                elif selected_index <= interval:
                                    info = candidate_infos[cur_page * interval + selected_index - 1]
                                else:
                                    selected_index = -1
                                    print('Index out of range')
                            else:
                                print('Invalid command')
                    break
            # Try to parsing bibtex
            if info is None:
                f.write('\n')
                f.flush()
                missing_bibs[citekey] = query
                logging.warning(f'{prefix} {citekey:20s} >> Failed')
            else:
                try:
                    bib_entry = BibEntry(citekey, info)
                except Exception as e:
                    f.write('\n')
                    f.flush()
                    missing_bibs[citekey] = query
                    logging.warning(str(e))
                else:
                    f.write(bib_entry.to_string(args.output[-3:], args.keep_empty_field) + '\n')
                    f.flush()
                    missing_fileds = bib_entry.get_missing_fileds()
                    if len(missing_fileds) > 0:
                        logging.warning('Missing {' + ', '.join(missing_fileds) + '}')
                    else:
                        logging.info('Complete fields')
    f.close()
    if len(missing_bibs) > 0:
        missing_file_path = os.path.join(os.path.dirname(args.output), 'missing_' + os.path.basename(args.output)[:-3] + 'json')
        logging.info(f'Missing bib entries can be found in {missing_file_path}')
        with open(missing_file_path, 'w') as f:
            json.dump(missing_bibs, f, indent=4, sort_keys=True)

if __name__ == '__main__':
    run()
