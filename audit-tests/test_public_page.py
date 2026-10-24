"""Offline checks of the actual public HTML, not a deployment assertion."""
from __future__ import annotations
import base64
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import unittest

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.ids, self.scripts = [], [], []
        self.csp = ''
        self.in_script = False
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag == 'a': self.links.append(a.get('href', ''))
        if tag == 'meta' and a.get('http-equiv', '').lower() == 'content-security-policy': self.csp = a.get('content', '')
        if tag == 'script': self.in_script = True; self.scripts.append('')
    def handle_endtag(self, tag):
        if tag == 'script': self.in_script = False
    def handle_data(self, data):
        if self.in_script: self.scripts[-1] += data

class PublicPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (Path(__file__).resolve().parents[1] / 'index.html').read_text(encoding='utf-8')
        cls.page = Page(cls.text)
    def test_current_research_is_reachable(self):
        base = 'https://github.com/KingStephan18/research-portfolio/blob/main/'
        self.assertIn(base + 'security-research/README.md', self.page.links)
        self.assertIn(base + 'maintainer-security/README.md', self.page.links)
    def test_footer_version_is_current(self):
        self.assertNotIn('Portfolio edition 03', self.text)
        self.assertIn('Portfolio edition 4.2', self.text)
    def test_fragment_links_and_ids(self):
        self.assertEqual(len(self.page.ids), len(set(self.page.ids)))
        for href in self.page.links:
            if href.startswith('#') and len(href) > 1: self.assertIn(href[1:], self.page.ids)
    def test_inline_scripts_match_csp(self):
        self.assertTrue(self.page.scripts)
        for text in self.page.scripts:
            digest = base64.b64encode(hashlib.sha256(text.encode()).digest()).decode()
            self.assertIn("'sha256-" + digest + "'", self.page.csp)

if __name__ == '__main__':
    unittest.main()
