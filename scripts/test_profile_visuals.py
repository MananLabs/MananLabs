"""Offline checks for calculations and fail-safe generation; no fixture data is published."""
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch
import xml.etree.ElementTree as ET
import generate_github_dashboard as dashboard
from normalize_snake import normalize


def day(d, count):
    return {'date':d,'contributionCount':count}


class DashboardTests(unittest.TestCase):
    def test_graphql_failure_explains_cause_without_exposing_token(self):
        from io import BytesIO
        response=BytesIO(b'{"errors":[{"message":"Field example is unavailable test-secret"}]}')
        with (patch.dict('os.environ',{'GITHUB_TOKEN':'test-secret'}),
              patch.object(dashboard.urllib.request,'urlopen',return_value=response)):
            with self.assertRaises(RuntimeError) as caught:
                dashboard.graphql('query {}',{})
        self.assertIn('Field example is unavailable',str(caught.exception))
        self.assertNotIn('test-secret',str(caught.exception))

    def test_today_may_still_be_empty(self):
        days=[day('2026-11-11',1),day('2026-11-12',2),day('2026-11-13',0)]
        self.assertEqual(dashboard.streaks(days,date(2026,11,13)),(2,2))

    def test_gap_breaks_streak(self):
        days=[day('2026-11-09',1),day('2026-11-11',1),day('2026-11-12',0),day('2026-11-13',3)]
        self.assertEqual(dashboard.streaks(days,date(2026,11,13)),(1,1))

    def test_empty_data(self):
        self.assertEqual(dashboard.streaks([],date(2026,11,13)),(0,0))

    def test_paginates_repositories(self):
        pages=[{'repositories':{'nodes':[{'stargazerCount':2}], 'pageInfo':{'hasNextPage':True,'endCursor':'next'}}},
               {'repositories':{'nodes':[{'stargazerCount':3}], 'pageInfo':{'hasNextPage':False,'endCursor':None}}}]
        with patch.object(dashboard,'graphql',side_effect=pages) as api:
            user,repos=dashboard.collect('MananLabs')
        self.assertEqual(len(repos),2)
        self.assertEqual(api.call_args_list[1].args[1]['cursor'],'next')

    def test_renders_safe_svg_and_empty_languages(self):
        user={'pullRequests':{'totalCount':3},'issues':{'totalCount':1},
              'contributionsCollection':{'totalCommitContributions':2,
                'contributionCalendar':{'totalContributions':6,'weeks':[{
                  'contributionDays':[day('2026-11-12',6)]}]}}}
        repos=[{'stargazerCount':4,'languages':{'edges':[]}}]
        images=dashboard.render(user,repos,date(2026,11,13))
        self.assertEqual(len(images),5)
        for svg in images.values():ET.fromstring(svg)
        self.assertIn('No public language data',images['languages.svg'])
        repos[0]['languages']['edges']=[{'size':100,'node':{'name':'A&B<script>','color':None}}]
        rendered=dashboard.render(user,repos,date(2026,11,13))['languages.svg']
        self.assertIn('A&amp;B&lt;script&gt;',rendered)
        self.assertIn('100.0%',rendered)

    def test_api_failure_preserves_last_cards(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp);card=output/'overview.svg';card.write_text('last-good')
            with (patch.object(dashboard,'OUT',output),
                  patch.object(dashboard,'collect',side_effect=RuntimeError('offline')),
                  patch('sys.argv',['generate_github_dashboard.py'])):
                with self.assertRaises(RuntimeError):dashboard.main()
            self.assertEqual(card.read_text(),'last-good')

    def test_snake_normalization_preserves_animation(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'source.svg';dest=Path(tmp)/'dest.svg'
            src.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="200"><style>@keyframes move{to{opacity:0}}</style><path d="M0 0"/></svg>')
            normalize(src,dest)
            root=ET.fromstring(dest.read_text())
            self.assertEqual(root.attrib['viewBox'],'0 0 1000 200')
            self.assertEqual(root.attrib['width'],'480')
            self.assertEqual(root.attrib['height'],'96.00')
            self.assertIn('@keyframes move',dest.read_text())


if __name__=='__main__':unittest.main()
