# -*- coding: utf-8 -*-

import requests
import json
import re
import os

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

    urls = {

        'journal': {
            'text': 'International Journals',
            'url': "https://dblp.org/search/publ/api?q=takahiro%20komamizu%20type%3AJournal_Articles%3A&h=1000&format=json"
        },

        'conference': {
            'text': 'International Conferences',
            'url': "https://dblp.org/search/publ/api?q=takahiro%20komamizu%20type%3AConference_and_Workshop_Papers%3A&h=1000&format=json"

        },

        'editor': {
            'text': 'Editor',
            'url': "https://dblp.org/search/publ/api?q=takahiro%20komamizu%20type%3AEditorship%3A&h=1000&format=json"
        },

        'preprint': {
            'text': 'Pre-Print',
            'url': "https://dblp.org/search/publ/api?q=takahiro%20komamizu%20type%3AInformal_and_Other_Publications%3A&h=1000&format=json"
        }

    }

    for style in urls:
        out.append(f"## {urls[style]['text']}")
        tmp_cont = getContent(urls[style]['url'], style)
        out.append('\n'.join(tmp_cont))

        if style != 'preprint':
            out.append("----")

    with open(os.path.join(PROJECT_ROOT, 'content', 'international.md'), 'w') as f:
        f.write('\n'.join(out))


def getContent(url, style):
    papers = getPapers(url, style)

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


def getPapers(url, style):
    cache_file = os.path.join(SCRIPT_DIR, 'international_tmp', f'{style}.json')

    try:
        print(f'Fetching {style} from remote...')
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        jdata = r.json()

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
