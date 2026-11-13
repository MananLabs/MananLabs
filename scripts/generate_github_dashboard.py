#!/usr/bin/env python3
"""Render local GitHub cards from authenticated public GitHub GraphQL data.

GITHUB_TOKEN=... python scripts/generate_github_dashboard.py
Without a token use --placeholders to create setup cards (never fake statistics).
No third-party statistics servers. Existing cards survive failed API requests.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from html import escape
import json
import os
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'dashboard'
ACCENT = '#5cf8a4'
CYAN = '#61dcec'
PURPLE = '#a085de'


def text(x, y, value, size=13, fill='#c9d5df', anchor='start'):
    return (f'<text x="{x}" y="{y}" font-family="ui-monospace,monospace" '
            f'font-size="{size}" fill="{fill}" text-anchor="{anchor}">{escape(str(value))}</text>')


def card(title, body, height=230, subtitle=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="{height}" '
            f'viewBox="0 0 480 {height}" role="img"><title>{escape(title)}</title>'
            f'<rect x=".5" y=".5" width="479" height="{height-1}" rx="12" '
            'fill="#080e14" stroke="#293a47"/>'
            + text(22, 32, title, 17, ACCENT)
            + text(22, 52, subtitle, 10, '#91a5b4') + body + '</svg>')


def placeholders():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, title in [('overview','GitHub overview'),('streak','Contribution streak'),
                        ('languages','Language distribution'),('activity','Contribution activity'),
                        ('milestones','Public account milestones')]:
        p = OUT / f'{name}.svg'
        if not p.exists():
            p.write_text(card(title, text(22, 95, 'Awaiting first GitHub Actions sync', 14, CYAN)
                              + text(22, 124, 'No statistics have been fetched yet.', 12)
                              + text(22, 152, 'Enable the Profile visuals workflow.', 12), 180))
    p = ROOT / 'assets' / 'contribution-snake.svg'
    if not p.exists():
        p.write_text(card('Contribution snake',text(22, 94, 'Awaiting real contribution data', 14, CYAN)
                          +text(22, 125, 'Run the Profile visuals workflow to generate.', 11), 155))


def graphql(query, variables):
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise RuntimeError('GITHUB_TOKEN is required; existing cards were preserved.')
    req = urllib.request.Request('https://api.github.com/graphql',
        data=json.dumps({'query': query, 'variables': variables}).encode(),
        headers={'Authorization': f'Bearer {token}', 'Content-Type':'application/json',
                 'User-Agent':'MananLabs-profile-dashboard'})
    with urllib.request.urlopen(req, timeout=45) as response:
        payload = json.load(response)
    if payload.get('errors'):
        # Avoid logging response data or authentication details.
        raise RuntimeError('GitHub GraphQL query failed; existing cards were preserved.')
    user = payload.get('data', {}).get('user')
    if not user:
        raise RuntimeError('GitHub user not found; existing cards were preserved.')
    return user


QUERY = '''query($login:String!, $cursor:String) {
 user(login:$login) {
  pullRequests { totalCount }
  issues { totalCount }
  contributionsCollection {
   totalCommitContributions
   contributionCalendar {
    totalContributions
    weeks { contributionDays { date contributionCount } }
   }
  }
  repositories(first:100, after:$cursor, ownerAffiliations:OWNER,
               privacy:PUBLIC, isFork:false) {
   pageInfo { hasNextPage endCursor }
   nodes { stargazerCount languages(first:100) {
    edges { size node { name color } }
   } }
  }
 }
}'''


def collect(login):
    cursor, repos, initial = None, [], None
    while True:
        user = graphql(QUERY, {'login':login,'cursor':cursor})
        initial = initial or user
        page = user['repositories']
        repos.extend(page['nodes'])
        if not page['pageInfo']['hasNextPage']:
            break
        cursor = page['pageInfo']['endCursor']
    return initial, repos


def streaks(days, today):
    """Today's empty cell doesn't end a streak until the UTC day finishes."""
    longest = run = 0
    by_date = {date.fromisoformat(d['date']):d['contributionCount'] for d in days}
    previous = None
    for day in sorted(by_date):
        run = (run + 1 if previous == day-timedelta(days=1) else 1) if by_date[day] else 0
        longest = max(longest,run)
        previous = day
    end = today if by_date.get(today,0) else today-timedelta(days=1)
    current = 0
    while by_date.get(end,0)>0:
        current += 1
        end -= timedelta(days=1)
    return current, longest


def render(user, repos, today=None):
    today = today or datetime.now(timezone.utc).date()
    collection = user['contributionsCollection']
    calendar = collection['contributionCalendar']
    days = [d for w in calendar['weeks'] for d in w['contributionDays']]
    stamp = f'Public data / refreshed {today.isoformat()} UTC'
    stars = sum(r['stargazerCount'] for r in repos)
    overview = ''
    metrics = [('Stars received',stars),('Commits / past year',collection['totalCommitContributions']),
               ('Pull requests / all time',user['pullRequests']['totalCount']),
               ('Issues / all time',user['issues']['totalCount']),
               ('Contributions / past year',calendar['totalContributions'])]
    icons = ['★','⌘','↗','◉','+']
    for i, ((label,value), icon) in enumerate(zip(metrics,icons)):
        y=86+i*33
        overview += text(22,y,icon,15,CYAN)+text(48,y,label,12)+text(452,y,f'{value:,}',18,ACCENT,'end')
    result={'overview.svg':card('GitHub overview',overview,250,stamp)}
    current,longest = streaks(days,today)
    body = '<circle cx="240" cy="118" r="44" fill="none" stroke="#293a47" stroke-width="3"/>'
    body += '<circle cx="240" cy="118" r="44" fill="none" stroke="#61dcec" stroke-width="3" stroke-dasharray="225 52" transform="rotate(-90 240 118)"/>'
    body += text(240,125,current,28,ACCENT,'middle')+text(240,180,'Current streak',12,CYAN,'middle')
    for x,v,l in [(82,calendar['totalContributions'],'Contributions'),(398,longest,'Longest streak')]:
        body+=text(x,123,f'{v:,}',24,ACCENT,'middle')+text(x,151,l,11,'#c9d5df','middle')
    body+=text(240,209,'Streaks measured within the past year (UTC)',10,'#91a5b4','middle')
    result['streak.svg']=card('Contribution streak',body,232,stamp)
    sizes=Counter(); colors={}
    for repo in repos:
        for edge in repo['languages']['edges']:
            n=edge['node'];sizes[n['name']]+=edge['size']; colors[n['name']]=n['color'] or PURPLE
    total=sum(sizes.values()); body=''; y=92
    top=sizes.most_common(6)
    if not total:
        body=text(22,98,'No public language data available.',13,CYAN)
    else:
        entries=[(n,v,colors[n]) for n,v in top]
        remaining=total-sum(v for _,v in top)
        if remaining:entries.append(('Other',remaining,'#64748b'))
        x=22.0
        for name,value,color in entries:
            width=436*value/total
            body+=f'<rect x="{x:.2f}" y="72" width="{width:.2f}" height="10" fill="{escape(color,quote=True)}"/>'
            x+=width
        for name,value,color in entries:
            y+=25
            body+=f'<circle cx="27" cy="{y-4}" r="4" fill="{escape(color,quote=True)}"/>'
            body+=text(42,y,name,12)+text(454,y,f'{value/total:.1%}',12,CYAN,'end')
    result['languages.svg']=card('Most-used languages',body,max(160,y+25),
                                 'Language bytes / owned public non-fork repositories')
    # Narrow weekly graph instead of a 53-column calendar; last 12 complete weeks.
    # It is an activity summary of real contributions, not a synthetic contribution grid.
    monday=today-timedelta(days=today.weekday())
    start=monday-timedelta(weeks=12)
    counts=[sum(d['contributionCount'] for d in days
                if start+timedelta(weeks=i)<=date.fromisoformat(d['date'])<start+timedelta(weeks=i+1))
            for i in range(12)]
    peak=max(counts,default=0) or 1
    body='<path d="M30 82 V191 H452" fill="none" stroke="#293a47"/>'
    for i,value in enumerate(counts):
        x=40+i*34;h=80*value/peak
        if value:
            body+=f'<rect x="{x}" y="{190-h:.1f}" width="20" height="{h:.1f}" rx="3" fill="{CYAN if i%2 else ACCENT}"/>'
        body+=text(x+10,183-h,value,9,'#c9d5df','middle')
    body+=text(30,214,start.strftime('%d %b'),10,'#91a5b4')
    body+=text(452,214,(monday-timedelta(days=1)).strftime('%d %b'),10,'#91a5b4','end')
    result['activity.svg']=card('Contribution activity',body,238,'Last 12 complete weeks / actual GitHub contributions')
    body=''
    for i,(label,val) in enumerate([('Public repositories',len(repos)),('Stars received',stars),
                                   ('Pull requests opened',user['pullRequests']['totalCount'])]):
        y=91+i*47
        body+=text(24,y,'◆',18,[ACCENT,CYAN,PURPLE][i])+text(50,y,label,12)+text(452,y,f'{val:,}',20,ACCENT,'end')
    result['milestones.svg']=card('Public account milestones',body,220,'Custom milestones / not official GitHub achievements')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--username',default='MananLabs')
    p.add_argument('--placeholders',action='store_true')
    args=p.parse_args()
    if args.placeholders:
        placeholders();return
    user,repos=collect(args.username)
    images=render(user,repos)
    # Finish all API calls and rendering before replacing any previous successful card.
    import xml.etree.ElementTree as ET
    for svg in images.values():ET.fromstring(svg)
    OUT.mkdir(parents=True,exist_ok=True)
    for name,svg in images.items():
        temporary=OUT/(name+'.tmp');temporary.write_text(svg);temporary.replace(OUT/name)
    print(f'Updated {len(images)} cards from public GitHub data.')


if __name__=='__main__':
    main()
