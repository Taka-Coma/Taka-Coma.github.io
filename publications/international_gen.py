# -*- coding: utf-8 -*-

import requests
import json
import re

with open('../data/awards.json', 'r') as f:
    data = json.load(f)

    awards = {}
    for row in data:
        if 'title' not in row['paper']:
            continue
        awards[f"{row['paper']['title']}.".lower()] =  row['award']

with open('./appendix.json', 'r') as f:
    adds = json.load(f)


def main():
    out = ['''---
title: "International"
date: 2020-10-20T22:24:46+09:00
draft: false
---
''']

    with open('./toappear.json', 'r') as f:
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
            #'url': "https://dblp.dagstuhl.de/search/publ/api?q=takahiro%20komamizu%20type%3AJournal_Articles%3A&h=1000&format=json"
        },

        'conference': {
            'text': 'International Conferences',
            'url': "https://dblp.org/search/publ/api?q=takahiro%20komamizu%20type%3AConference_and_Workshop_Papers%3A&h=1000&format=json"
            #'url': "https://dblp.dagstuhl.de/search/publ/api?q=takahiro%20komamizu%20type%3AConference_and_Workshop_Papers%3A&h=1000&format=json"

        },

        'editor': {
            'text': 'Editor',
            'url': "https://dblp.org/search/publ/api?q=takahiro%20komamizu%20type%3AEditorship%3A&h=1000&format=json"
        },

        'preprint': {
            'text': 'Pre-Print',
            'url': "https://dblp.org/search/publ/api?q=takahiro%20komamizu%20type%3AInformal_and_Other_Publications%3A&h=1000&format=json"
            #'url': "https://dblp.dagstuhl.de/search/publ/api?q=takahiro%20komamizu%20type%3AInformal_and_Other_Publications%3A&h=1000&format=json"
        }

    }

    for style in urls:
        out.append(f"## {urls[style]['text']}")
        tmp_cont = getContent(urls[style]['url'], style)
        out.append('\n'.join(tmp_cont))

        if style != 'preprint':
            out.append("----")

    with open('../content/international.md', 'w') as f:
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
        
    return out



def getPapers(url, style):
    try:
        r = requests.get(url, timeout=5)
        jdata = r.json()

        with open(f'./international_tmp/{style}.json', 'w') as w:
            json.dump(jdata, w)

    except:
        print('Time out: ', style)
        with open(f'./international_tmp/{style}.json', 'r') as r:
            jdata = json.load(r)

    data = jdata['result']['hits']['hit']

    if style == 'conference':
        out = {}
        for d in data:
            paper = d['info']

            if paper['year'] not in out:
                out[paper['year']] = []
            out[paper['year']].append(paper)

        with open('./additional_papers.json', 'r') as f:
            data = json.load(f)

            for paper in data:
                if paper['type'] != 'conference':
                    continue
                if paper['year'] not in out:
                    out[paper['year']] = []
                out[paper['year']].append(paper)
                
        return dict(sorted(out.items(), key=lambda x:x[0], reverse=True))

    else:
        out = []
        for d in data:
            out.append(d['info'])

        with open('./additional_papers.json', 'r') as f:
            add = json.load(f)
            for paper in add:
                if paper['type'] != style:
                    continue
                out.append(paper)

        return sorted(out, key=lambda x:x['year'], reverse=True)



if __name__ == "__main__":
    main()
