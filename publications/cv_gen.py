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
    out = []

    with open('./toappear.json', 'r') as f:
        data = json.load(f)
        if len(data) > 0:
            out.append("## To Appear")
        for paper in data:
            out.append('\item ' + formatPaper(paper, style=paper['type']))
        
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
        }
    }

    for style in urls:
        out.append("## " + urls[style]['text'])
        tmp_cont = getContent(urls[style]['url'], style)
        out.append('\n'.join(tmp_cont))

    with open('./cv.txt', 'w') as f:
        f.write('\n'.join(out))


def getContent(url, style):
    papers = getPapers(url, style)

    out = []

    if style == 'conference':
        for year in papers:
            tmp_cont = []
            for paper in papers[year]:
                tmp_cont.append(formatPaper(paper, style=style))
            out.append('\item ' + '\n\item '.join(tmp_cont))
    else:
        tmp_cont = [formatPaper(paper, style=style) for paper in papers]
        out.append('\item ' + '\n\item '.join(tmp_cont))

    return out


def formatPaper(paper, style='journal'):
    if isinstance(paper['authors']['author'], dict) :
        authors = "\\underline{" + abbreviate_name(paper['authors']['author']['text']) + "}"
    else:
        authors = ', '.join(["\\underline{" + abbreviate_name(a['text']) + "}"
            if a['text'] == 'Takahiro Komamizu'
            else abbreviate_name(re.sub(r' 000\d', '', a['text'])) for a in paper['authors']['author']])

    out = f"{authors}, \"{paper['title'][:-1].replace(' - ', ': ').replace('&apos;', '\'')}\", {paper['venue'].replace('&', '\\&')}"

    if "volume" in paper:
        out += f", Vol.{paper['volume']}"

    if "number" in paper:
        out += f", No.{paper['number']}"

    if 'pages' in paper:
        out += f", pp.{paper['pages']}"

    out += f", {paper['year']}"

#    if 'ee' in paper:
#        if 'key' in paper:
#            if paper['key'] in adds:
#                out += f" ([DOI]({paper['ee']})"
#                for cont in adds[paper['key']]:
#                    if adds[paper['key']][cont][:4] == 'http':
#                        out += f", [{cont}]({adds[paper['key']][cont]})"
#                    else:
#                        out += f", [{cont}](/pdfs/{adds[paper['key']][cont]})"
#                out += ")"
#            else:
#                out += f" ([DOI]({paper['ee']}))"
#        else:
#            out += f" ([DOI]({paper['ee']}))"


    if paper['title'].lower() in awards and style != 'preprint':
        out += ' -- {\\color{red} ' + awards[paper['title'].lower()] + '}'
        
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


def abbreviate_name(full_name: str) -> str:
    parts = full_name.strip().split()
    initials = " ".join([p[0].upper() + "." for p in parts[:-1]])
    last_name = parts[-1].capitalize()
    return f"{initials} {last_name}"



if __name__ == "__main__":
    main()
