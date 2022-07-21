# -*- coding: utf-8 -*-

import requests
import json

def main():
    out = ['''---
title: "Domestic"
date: 2020-10-20T22:24:46+09:00
draft: false
---
''']

    with open('./domestic_toappear.json', 'r') as f:
        data = json.load(f)
        if len(data) > 0:
            out.append("## 採択済み")
            for paper in data:
                out.append('- ' + formatPaper(paper, style=paper['type']))
            out.append("----")

    urls = {
        'journal': {
            'text': '論文誌',
            'url': "./domestic_journal.json"
        },
        'ref_conference': {
            'text': '査読あり会議',
            'url': "./domestic_refconf.json",
        },
        'nonref_conference': {
            'text': '査読なし会議',
            'url': "./domestic_nonrefconf.json"
        },
        'invited': {
            'text': '招待講演',
            'url': "./domestic_invited.json",
        },
        'article': {
            'text': '寄稿',
            'url': "./domestic_article.json"
        },
        'edit': {
            'text': '編集',
            'url': "./domestic_edit.json"
        },
        'technical': {
            'text': '技術紀要',
            'url': "./domestic_technical.json"
        }
    }

    for style in urls:
        out.append(f"## {urls[style]['text']}")
        tmp_cont = getContent(urls[style]['url'], style)
        out.append('\n'.join(tmp_cont))

        if style != 'technical':
            out.append("----")

    with open('../content/domestic.md', 'w') as f:
        f.write('\n'.join(out))


def getContent(url, style):
    papers = getPapers(url, style)

    out = []

    if style == 'nonref_conference':
        for year in papers:
            out.append(f"### {year}")
            tmp_cont = []
            for paper in papers[year]:
                tmp_cont.append(formatPaper(paper, style=style))
            out.append('- ' + '\n- '.join(tmp_cont))
    else:
        tmp_cont = [formatPaper(paper, style=style) for paper in papers]
        out.append('- ' + '\n- '.join(tmp_cont))

    return out


def formatPaper(paper, style='journal'):
    authors = ', '.join([f"[{a['text']}](/)" if a['text'] == 'Takahiro Komamizu' or a['text'] == '駒水 孝裕'  else a['text'] for a in paper['authors']['author']])

    out = f"{authors}, \"{paper['title']}\", {paper['venue']}"

    if 'volume' in paper:
        out += f", Vol.{paper['volume']}, No.{paper['number']}"

    if 'pages' in paper:
        out += f", pp.{paper['pages']}"

    out += f", {paper['year']}"

    if 'month' in paper:
        out += f".{paper['month']}"

    if 'ee' in paper:
        if 'slide' in paper:
            out += f" ([link]({paper['ee']}), [slide]({paper['slide']}))"
        else:
            if style == 'journal':
                out += f" ([DOI]({paper['ee']}))"
            else:
                out += f" ([link]({paper['ee']}))"

    elif 'slide' in paper:
        out += f" ([slide]({paper['slide']}))"

    if 'awards' in paper:
        tmp_cont = ['{{< awards name="' + award['name'] + '" url="' + award['url'] + '" >}}' for award in paper['awards']]
        out += " -- " + ', '.join(tmp_cont)
        
    return out



def getPapers(url, style):
    data = []
    with open(url, 'r') as f:
        data = json.load(f)

    if style == 'nonref_conference':
        out = {}
        for paper in data:
            if paper['year'] not in out:
                out[paper['year']] = []
            out[paper['year']].append(paper)

        return dict(sorted(out.items(), key=lambda x:x[0], reverse=True))

    else:
        return data


if __name__ == "__main__":
    main()
