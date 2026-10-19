# -*- coding: utf-8 -*-

import requests
import json
import re
import os
import time

# Minimum delay (seconds) between consecutive requests to DBLP, and how long
# to back off when it responds with 429 (Too Many Requests).
REQUEST_DELAY_SECONDS = 5
RATE_LIMIT_RETRIES = 3
RATE_LIMIT_BACKOFF_SECONDS = 15

# dblp's search API (dblp.org/search/publ/api) sits behind an Anubis bot
# challenge and answers scripts with an HTML page, so query the SPARQL
# endpoint by author PID instead.
SPARQL_ENDPOINT = 'https://sparql.dblp.org/sparql'
AUTHOR_PID = '60/10773'

STYLES = {
    'journal': {'text': 'International Journals', 'rdf_type': 'Article'},
    'conference': {'text': 'International Conferences', 'rdf_type': 'Inproceedings'},
    'editor': {'text': 'Editor', 'rdf_type': 'Editorship'},
    'preprint': {'text': 'Pre-Print', 'rdf_type': 'Informal'},
}

SPARQL_QUERY = f'''PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?publ ?type ?title ?venue ?year ?pages ?volume ?number ?ee ?stream ?ord ?name WHERE {{
  ?publ dblp:authoredBy|dblp:editedBy <https://dblp.org/pid/{AUTHOR_PID}> ;
        a ?type ; dblp:title ?title ; dblp:hasSignature ?sig .
  ?sig dblp:signatureOrdinal ?ord ; dblp:signatureDblpName ?name .
  VALUES ?type {{ {' '.join('dblp:' + s['rdf_type'] for s in STYLES.values())} }}
  OPTIONAL {{ ?publ dblp:yearOfEvent ?eventYear }}
  OPTIONAL {{ ?publ dblp:yearOfPublication ?publYear }}
  BIND(COALESCE(?eventYear, ?publYear) AS ?year)
  OPTIONAL {{ ?publ dblp:publishedIn ?venue }}
  OPTIONAL {{ ?publ dblp:pagination ?pages }}
  OPTIONAL {{ ?publ dblp:publishedInJournalVolume ?volume }}
  OPTIONAL {{ ?publ dblp:publishedInJournalVolumeIssue ?number }}
  OPTIONAL {{ ?publ dblp:primaryDocumentPage ?ee }}
  OPTIONAL {{ ?publ dblp:publishedInStream/dblp:streamTitle ?stream }}
}}'''

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

with open(os.path.join(PROJECT_ROOT, 'data', 'awards.json'), 'r') as f:
    data = json.load(f)

    awards = {}
    for row in data:
        if 'title' not in row['paper']:
            continue
        awards[f"{row['paper']['title']}.".lower()] =  row['award']

with open(os.path.join(SCRIPT_DIR, 'appendix.json'), 'r') as f:
    adds = json.load(f)


def main():
    out = ['''---
title: "International"
date: 2020-10-20T22:24:46+09:00
draft: false
---
''']

    with open(os.path.join(SCRIPT_DIR, 'toappear.json'), 'r') as f:
        data = json.load(f)
        if len(data) > 0:
            out.append("## To Appear")
        for paper in data:
            out.append('1. ' + formatPaper(paper, style=paper['type']))

    if len(data) > 0:
        out.append("----")

    for style in STYLES:
        out.append(f"## {STYLES[style]['text']}")
        tmp_cont = getContent(style)
        out.append('\n'.join(tmp_cont))

        if style != 'preprint':
            out.append("----")

    with open(os.path.join(PROJECT_ROOT, 'content', 'international.md'), 'w') as f:
        f.write('\n'.join(out))


def getContent(style):
    papers = getPapers(style)

    out = []

    if style == 'conference':
        for year in papers:
            out.append(f"### {year}")
            tmp_cont = []
            for paper in papers[year]:
                tmp_cont.append(formatPaper(paper, style=style))
            out.append('1. ' + '\n1. '.join(tmp_cont))
    else:
        tmp_cont = [formatPaper(paper, style=style) for paper in papers]
        out.append('1. ' + '\n1. '.join(tmp_cont))

    return out


def formatPaper(paper, style='journal'):
    if isinstance(paper['authors']['author'], dict) :
        authors = f"[{paper['authors']['author']['text']}](/)"
    else:
        authors = ', '.join([f"[{a['text']}](/)"
            if a['text'] == 'Takahiro Komamizu'
            else re.sub(r' 000\d', '', a['text']) for a in paper['authors']['author']])

    out = f"{authors}, \"{paper['title'][:-1].replace(' - ', ': ')}\", {paper['venue']}"

    if "volume" in paper:
        if style == 'preprint':
            out += f", {paper['volume']}"
        else:
            out += f", Vol.{paper['volume']}"

    if "number" in paper:
        out += f", No.{paper['number']}"

    if 'pages' in paper:
        out += f", pp.{paper['pages']}"

    out += f", {paper['year']}"

    if 'ee' in paper:
        if 'key' in paper:
            if paper['key'] in adds:
                out += f" ([DOI]({paper['ee']})"
                for cont in adds[paper['key']]:
                    if adds[paper['key']][cont][:4] == 'http':
                        out += f", [{cont}]({adds[paper['key']][cont]})"
                    else:
                        out += f", [{cont}](/pdfs/{adds[paper['key']][cont]})"
                out += ")"
            else:
                out += f" ([DOI]({paper['ee']}))"
        else:
            out += f" ([DOI]({paper['ee']}))"


    if paper['title'].lower() in awards and style != 'preprint':
        out += ' --- {{< awards name="' + awards[paper['title'].lower()] + '" >}}'

    if 'note' in paper:
        out += ' --- ' + paper['note']

    return out



def getFirstAuthor(paper):
    """Get the first author's name for sorting"""
    if 'authors' not in paper or 'author' not in paper['authors']:
        return ''

    author = paper['authors']['author']
    if isinstance(author, dict):
        return author.get('text', '')
    elif isinstance(author, list) and len(author) > 0:
        return author[0].get('text', '')
    return ''


def getVenue(paper):
    """Get the venue name for sorting"""
    return paper.get('venue', '')


def normalizeTitle(title):
    """Normalize title for duplicate detection"""
    if not title:
        return ''
    # Remove trailing period, convert to lowercase, strip whitespace
    normalized = title.lower().strip()
    if normalized.endswith('.'):
        normalized = normalized[:-1]
    return normalized


def fetchWithRateLimit(url, params=None, headers=None):
    """GET url, backing off and retrying when DBLP responds with 429."""
    throttleRequest()

    for attempt in range(RATE_LIMIT_RETRIES + 1):
        r = requests.get(url, params=params, headers=headers, timeout=60)

        if r.status_code != 429:
            r.raise_for_status()
            return r

        if attempt == RATE_LIMIT_RETRIES:
            r.raise_for_status()

        wait = int(r.headers.get('Retry-After', RATE_LIMIT_BACKOFF_SECONDS * (attempt + 1)))
        print(f'  ⚠ Rate limited (429), retrying in {wait}s...')
        time.sleep(wait)


def throttleRequest():
    """Ensure at least REQUEST_DELAY_SECONDS pass between requests in this process."""
    now = time.monotonic()
    if throttleRequest.last_request_at is not None:
        elapsed = now - throttleRequest.last_request_at
        if elapsed < REQUEST_DELAY_SECONDS:
            time.sleep(REQUEST_DELAY_SECONDS - elapsed)
    throttleRequest.last_request_at = time.monotonic()


throttleRequest.last_request_at = None


def fetchAllPapers():
    """Run the SPARQL query once and group the records by style, in the
    same {'result': {'hits': {'hit': [{'info': ...}]}}} shape that the
    dblp search API returned (and that the cache files hold)."""
    if fetchAllPapers.result is not None:
        return fetchAllPapers.result

    r = fetchWithRateLimit(SPARQL_ENDPOINT, params={'query': SPARQL_QUERY},
                           headers={'Accept': 'application/sparql-results+json'})

    records = {}
    for row in r.json()['results']['bindings']:
        v = {k: x['value'] for k, x in row.items()}
        rec = records.setdefault(v['publ'], {'row': v, 'authors': {}})
        rec['authors'][int(v['ord'])] = v['name']

    type_to_style = {s['rdf_type']: style for style, s in STYLES.items()}
    result = {style: [] for style in STYLES}
    for publ, rec in sorted(records.items()):
        v = rec['row']
        style = type_to_style[v['type'].split('#')[-1]]
        key = publ.removeprefix('https://dblp.org/rec/')
        cached = cachedInfo(style, key)

        paper = {
            'authors': {'author': [{'text': rec['authors'][o]} for o in sorted(rec['authors'])]},
            'title': v['title'],
        }
        if 'venue' in v:
            # "DEXA (2)" -> "DEXA", as the search API reported it
            paper['venue'] = re.sub(r'\s*\([^)]*\)$', '', v['venue'])
        else:
            # Editorships have no venue in the RDF; the search API gave e.g. "ICDAR@ICMR"
            paper['venue'] = cached.get('venue') or streamAcronym(v.get('stream', ''))
        for field in ('volume', 'number', 'pages'):
            if field in v:
                paper[field] = v[field]
        paper['year'] = v['year']
        paper['key'] = key
        if 'ee' in v:
            # The RDF upper-cases DOIs; keep the original casing when already known
            cached_ee = cached.get('ee')
            if isinstance(cached_ee, str) and cached_ee.lower() == v['ee'].lower():
                paper['ee'] = cached_ee
            else:
                paper['ee'] = v['ee']

        result[style].append({'info': paper})

    fetchAllPapers.result = {style: {'result': {'hits': {'hit': hits}}}
                             for style, hits in result.items()}
    return fetchAllPapers.result


fetchAllPapers.result = None


def cachedInfo(style, key):
    """Record for key in the previous cache file, or {} if absent."""
    if style not in cachedInfo.cache:
        try:
            with open(os.path.join(SCRIPT_DIR, 'international_tmp', f'{style}.json'), 'r') as f:
                hits = json.load(f)['result']['hits']['hit']
            cachedInfo.cache[style] = {h['info'].get('key'): h['info'] for h in hits}
        except (OSError, ValueError, KeyError):
            cachedInfo.cache[style] = {}
    return cachedInfo.cache[style].get(key, {})


cachedInfo.cache = {}


def streamAcronym(stream_title):
    """"Workshop on ... (NarSUM)" -> "NarSUM"."""
    m = re.search(r'\(([^)]*)\)$', stream_title)
    return m.group(1) if m else stream_title


def getPapers(style):
    cache_file = os.path.join(SCRIPT_DIR, 'international_tmp', f'{style}.json')

    try:
        print(f'Fetching {style} from remote...')
        jdata = fetchAllPapers()[style]

        # Save to cache
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'w') as w:
            json.dump(jdata, w)
        print(f'  ✓ Successfully fetched {style}')

    except Exception as e:
        print(f'  ✗ Failed to fetch {style}: {e}')
        print(f'  → Loading from cache: {cache_file}')
        try:
            with open(cache_file, 'r') as r:
                jdata = json.load(r)
            print(f'  ✓ Successfully loaded from cache')
        except Exception as cache_error:
            print(f'  ✗ Failed to load from cache: {cache_error}')
            raise

    data = jdata['result']['hits']['hit']

    if style == 'conference':
        out = {}
        seen_titles = set()  # Track titles to avoid duplicates

        for d in data:
            paper = d['info']
            title_key = normalizeTitle(paper.get('title', ''))

            if title_key:
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    if paper['year'] not in out:
                        out[paper['year']] = []
                    out[paper['year']].append(paper)
                else:
                    print(f'  ⚠ Duplicate found (remote): "{paper.get("title", "")}"')

        with open(os.path.join(SCRIPT_DIR, 'additional_papers.json'), 'r') as f:
            data = json.load(f)

            for paper in data:
                if paper['type'] != 'conference':
                    continue

                title_key = normalizeTitle(paper.get('title', ''))
                if title_key:
                    if title_key not in seen_titles:
                        seen_titles.add(title_key)
                        if paper['year'] not in out:
                            out[paper['year']] = []
                        out[paper['year']].append(paper)
                    else:
                        print(f'  ⚠ Duplicate found (local): "{paper.get("title", "")}"')

        # Sort by year (descending), then by venue, then by first author within each year
        for year in out:
            out[year] = sorted(out[year], key=lambda x: (getVenue(x), getFirstAuthor(x)))

        return dict(sorted(out.items(), key=lambda x:x[0], reverse=True))

    else:
        out = []
        seen_titles = set()  # Track titles to avoid duplicates

        for d in data:
            paper = d['info']
            title_key = normalizeTitle(paper.get('title', ''))

            if title_key:
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    out.append(paper)
                else:
                    print(f'  ⚠ Duplicate found (remote): "{paper.get("title", "")}"')

        with open(os.path.join(SCRIPT_DIR, 'additional_papers.json'), 'r') as f:
            add = json.load(f)
            for paper in add:
                if paper['type'] != style:
                    continue

                title_key = normalizeTitle(paper.get('title', ''))
                if title_key:
                    if title_key not in seen_titles:
                        seen_titles.add(title_key)
                        out.append(paper)
                    else:
                        print(f'  ⚠ Duplicate found (local): "{paper.get("title", "")}"')

        # Sort by year (descending), then by venue, then by first author
        return sorted(out, key=lambda x: (int(x['year']) * -1, getVenue(x), getFirstAuthor(x)))



if __name__ == "__main__":
    main()
