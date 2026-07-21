# -*- coding: utf-8 -*-

import json

def main():
    out = ['''---
title: "Domestic"
date: 2020-10-20T22:24:46+09:00
draft: false
---
''']

    print('Processing 採択済み...')
    with open('./domestic_toappear.json', 'r') as f:
        data = json.load(f)
        print(f'  ✓ Loaded {len(data)} paper(s)')
        if len(data) > 0:
            out.append("## 採択済み")
            for paper in data:
                out.append('1. ' + formatPaper(paper, style=paper['type']))
            out.append("----")

    urls = {
        'invited': {
            'text': '講演',
            'url': "./domestic_invited.json",
        },
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
        'students_conference': {
            'text': '査読なし会議（学生発表）',
            'url': "./domestic_students.json"
        },
        'article': {
            'text': '寄稿',
            'url': "./domestic_article.json"
        },
        'edit': {
            'text': '編集',
            'url': "./domestic_edit.json"
        },
        'press': {
            'text': 'プレスリリース',
            'url': "./domestic_press.json"
        },
        'technical': {
            'text': '技術紀要',
            'url': "./domestic_technical.json"
        }
    }

    for style in urls:
        print(f"Processing {urls[style]['text']}...")
        out.append(f"## {urls[style]['text']}")
        tmp_cont = getContent(urls[style]['url'], style)
        out.append('\n'.join(tmp_cont))

        if style != 'technical':
            out.append("----")

    print('Writing ../content/domestic.md...')
    with open('../content/domestic.md', 'w') as f:
        f.write('\n'.join(out))
    print('  ✓ Done')


def getContent(url, style):
    papers = getPapers(url, style)

    out = []

    if style == 'nonref_conference':
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
    authors = ', '.join([f"[{a['text']}](/)" if a['text'] == 'Takahiro Komamizu' or a['text'] == '駒水 孝裕'  else a['text'] for a in paper['authors']['author']])

    if 'url' in paper:
        venue = f"[{paper['venue']}]({paper['url']})"
    else:
        venue = paper['venue']

    parts = [authors, f"\"{paper['title']}\"", venue]

    if 'volume' in paper:
        parts.append(f"Vol.{paper['volume']}")

    if 'number' in paper:
        parts.append(f"No.{paper['number']}")

    if 'pages' in paper:
        parts.append(f"pp.{paper['pages']}")

    year = str(paper['year'])
    if 'month' in paper:
        year += f".{paper['month']}"
    parts.append(year)

    out = ', '.join(parts)

    additional = []

    if paper.get('ee'):
        additional.append(f"[DOI]({paper['ee']})" if style == 'journal' else f"[link]({paper['ee']})")

    if 'slide' in paper:
        additional.append(f"[slide]({paper['slide']})")

    if 'resources' in paper:
        for res in paper['resources']:
            additional.append(f"[resource]({res})")

    if additional:
        out += f" ({', '.join(additional)})"

    if 'awards' in paper:
        awards = ', '.join('{{< awards name="' + award['name'] + '" url="' + award['url'] + '" >}}' for award in paper['awards'])
        out += f" -- {awards}"

    if 'note' in paper:
        out += f" ({paper['note']})"

    return out



def getPapers(url, style):
    data = []
    with open(url, 'r') as f:
        data = json.load(f)
    print(f'  ✓ Loaded {len(data)} paper(s) from {url}')

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
