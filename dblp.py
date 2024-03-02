import re
import requests
from bs4 import BeautifulSoup

import venue


DBLP_BASE_URL = 'https://dblp.uni-trier.de/'
DBLP_PUBLICATION_SEARCH_URL = DBLP_BASE_URL + 'search/publ/api'
DBLP_PUBLICATION_PROCEEDING_URL = DBLP_BASE_URL + 'db/conf'


class DblpSearchResults:
    """
    Results of one search in DBLP.
    """

    def __init__(self, json):
        self.json = json
        result = json["result"]
        self.query = result["query"]
        status = result["status"]
        self.status_code = int(status["@code"])
        self.status_text = status["text"]
        hits = result["hits"]
        self.total_matches = int(hits["@total"])
        self.results = []
        if self.total_matches > 0:
            self.results = [
                {"score": hit_json["@score"], "info": hit_json["info"]} 
                for hit_json in hits["hit"]
            ]


def perform_request(url, params=None, **kwargs):
    """
    Perform a GET request to DBLP.
    :param url: URL to access.
    :param params: Optional parameters.
    :param kwargs: Optional arguments.
    :return: Response.
    :raises: HTTPError if request was unsuccessful.
    """
    response = requests.get(url, params=params, timeout=(3,5), **kwargs)
    if response.status_code == 200:
        return response
    else:
        response.raise_for_status()
        return None


def search_publication(query, max_search_results=30):
    """
    Search for publication according to given query.
    :param pub_query: Query for publication.
    :param max_search_results: Maximal number of search results to return.
    :return: Search results.
    """
    parameters = dict(
        q=query,
        format="json",
        h=max_search_results
    )
    
    try:
        response = perform_request(DBLP_PUBLICATION_SEARCH_URL, params=parameters)
        search_results = DblpSearchResults(response.json())
    except Exception as e:
        return (None, str(e))
    else:
        candidates = sorted(search_results.results, key=lambda x: x['score'], reverse=True)
        candidate_infos = []
        for candidate in candidates:
            if 'arxiv' not in candidate['info']['ee'].lower():
                candidate_infos.append(candidate['info'])
            elif len(candidate_infos) == 0:
                candidate_infos.append(candidate['info'])
        return (candidate_infos, 'Found')
        
        
def search_proceeding_address(venue, year):
    """
    Search for proceeding address according to given query.
    :param pub_query: Query for proceeding.
    :param max_search_results: Maximal number of search results to return.
    :return: Search results.
    """
    try:
        response = perform_request(DBLP_PUBLICATION_PROCEEDING_URL + '/' + venue)
        bs = BeautifulSoup(response.content.decode(), 'html.parser')
        element = bs.find_all(id=year)[0]
        element_strs = ''.join(element.strings)
        address = element_strs.split(':')[-1].strip()
        return (address, 'Found')
    except Exception as e:
        return (None, str(e))


def extract_name(name):
    """
    extract pure text of author name by removing digit postfix, which denotes sub-id of author with the same name
    """
    pattern = re.compile(r'\s*\d+\s*')
    return pattern.sub('', name)


def search_publication_by_venue(venue_name, year, pubtype, max_search_results=5):
    """
    Search dblp directly.
    :param pub_query: Query string.
    e.g., streamid:conf/uss: year:2023: type:Conference_and_Workshop_Papers: 
    :param max_search_results: Maximal number of search results to return.
    :return: Search results.
    """
    if pubtype == venue.PubType.PROCEEDING:
        venue_prefix = 'conf'
        pub_class = 'inproceedings'
    elif pubtype == venue.PubType.JOURNAL:
        venue_prefix = 'journals'
        pub_class = 'article'
    else:
        venue_prefix = 'journals'
        pub_class = 'informal'
    pubtype_str = pubtype.value.replace(" ", "_")
    query = f'streamid:{venue_prefix}/{venue_name}: year:{year}: type:{pubtype_str}:'
    parameters = dict(
        q=query,
        h=max_search_results
    )
    
    try:
        response = perform_request(DBLP_BASE_URL, params=parameters)
        bs = BeautifulSoup(response.content.decode(), 'html.parser')
        pubs = list(filter(
            lambda e: f'{venue_prefix}/{venue_name}' in e['id'],
            bs.select(f'li.entry.{pub_class}.toc')
        ))
        titles = [pub.select('.title')[0].get_text()[:-1] for pub in pubs]
        if len(titles) > 0:
            return (titles, 'Found')
        else:
            return (None, 'Empty')
    except Exception as e:
        return (None, str(e))
        