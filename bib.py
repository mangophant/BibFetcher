import html
import re
from venue import PubType, venue_dict
from dblp import search_proceeding_address, extract_name


class BibEntry:
    
    bib_item_dict = {
        PubType.PROCEEDING: ['author', 'title', 'booktitle', 'pages', 'address', 'year'],
        PubType.JOURNAL: ['author', 'title', 'journal', 'volume', 'number', 'pages', 'year'],
        PubType.ARXIV: ['author', 'title', 'journal', 'volume', 'year']
    }
    
    def __init__(self, citekey, info) -> None:
        self.citekey = citekey
        self.type = PubType(info['type'])
        self.bib = {}
        self.bib['title'] = title_case(html.unescape(info['title'][:-1]))
        authors = info['authors']['author']
        if isinstance(authors, dict):
            self.bib['author'] = [extract_name(authors['text'])]
        else:
            self.bib['author'] = [extract_name(author['text']) for author in authors]
        self.bib['year'] = info['year']
        venue_abbr = info['url'].split('/')[-2]
        venue = venue_dict[self.type].get(venue_abbr)
        if venue is None:
            venue = info['venue']
            # raise Exception(f'Not supported venue: {venue_abbr}!')
        if self.type == PubType.PROCEEDING:
            self.bib['booktitle'] = 'Proceedings of ' + venue
            self.bib['address'], _ = search_proceeding_address(venue_abbr, self.bib['year'])
            self.bib['pages'] = info.get('pages')
        else:
            self.bib['journal'] = venue
            self.bib['volume'] = info.get('volume')
            if self.type == PubType.JOURNAL:
                self.bib['number'] = info.get('number')
                self.bib['pages'] = info.get('pages')
    
    def to_text(self, keep_empty_field) -> str:
        bib_items = []
        for k in self.bib_item_dict[self.type]:
            if self.bib[k] is not None:
                if k == 'title':
                    bib_items.append(f'"{self.bib[k]}"')
                elif k == 'author':
                    if len(self.bib[k]) > 2:
                        bib_items.append(', '.join(self.bib[k][:-2] + [' and '.join(self.bib[k][-2:])]))
                    else:
                        bib_items.append(' and '.join(self.bib[k]))
                elif k == 'booktitle':
                    bib_items.append('in ' + self.bib[k])
                elif k == 'pages':
                    bib_items.append('pp.' + self.bib[k])
                elif k == 'volume':
                    bib_items.append('vol.' + self.bib[k])
                elif k == 'number':
                    bib_items.append('no.' + self.bib[k])
                else:
                    bib_items.append(self.bib[k])
            elif keep_empty_field:
                bib_items.append('')
        return ', '.join(bib_items).replace('{', '').replace('}', '') + '.'
    
    def to_bibtex(self, keep_empty_field) -> str:
        bibtex_str = '@inproceedings' if self.type == PubType.PROCEEDING else '@article'
        bibtex_str += '{' + self.citekey + ',\n'
        postfix = '},\n'
        for k in self.bib_item_dict[self.type]:
            prefix = '\t' + k + '= {'
            if self.bib[k] is not None:
                if k == 'title':
                    payload = '{' + self.bib[k] + '}'
                elif k == 'author':
                    if len(self.bib[k]) > 2:
                        payload = ', '.join(self.bib[k][:-2] + [' and '.join(self.bib[k][-2:])])
                    else:
                        payload = ' and '.join(self.bib[k])
                else:
                    payload = self.bib[k]
            elif keep_empty_field:
                payload = ''
            bibtex_str += prefix + payload + postfix
        bibtex_str += '}\n'
        return bibtex_str
    
    def to_string(self, format, keep_empty_field=False) -> str:
        if format == 'bib':
            return self.to_bibtex(keep_empty_field)
        elif format == 'txt':
            return self.to_text(keep_empty_field)
        else:
            raise Exception('Invalid output format!')
        
    def get_missing_fileds(self) -> str:
        missing_fileds = list(filter(lambda k: self.bib[k] is None, self.bib_item_dict[self.type]))
        return missing_fileds
    
    
def info2str(info):
    authors = info['authors']['author']
    if isinstance(authors, dict):
        auhtor_names = extract_name(authors['text'])
    else:
        auhtor_names = ', '.join([extract_name(author['text']) for author in authors])
    return '\n'.join([
        'Title: ' + info['title'],
        '    Auhtor: ' + auhtor_names,
        f"    Venue: {info['venue']} {info['year']}"
    ])
    

DO_NOT_TITLE = [
    "a", "an", "and", "as", "at", "be", "but", "by", "en", "for", "from", "if",
    "in", "is", "nor", "of", "on", "or", "per", "the", "through", "to", "v", "vs", "via", "with"
]


def title_word(chunk):
    """Title-case a given word (or do noting to a non-word chunk)."""
    if chunk.lower() in DO_NOT_TITLE:
        return chunk.lower()
    return chunk[0].upper() + chunk[1:].lower()


def title_case(value):
    words_and_nonword_chunks = re.split(r"""
        (                   # capture both words and the chunks between words
            (?:             # split on consecutive:
                \s |        # - whitespace characters
                -  |        # - dashes
                :  |        # - colons
                "  |        # - double quotes
                [\[({<]     # - opening brackets and braces
            )+
        )
    """, value, flags=re.VERBOSE)
    return "".join(
        # upper/lower-casing symbols and whitespace does nothing
        title_word(chunk)
        for chunk in words_and_nonword_chunks
    )