#!/usr/bin/env python3
"""Check catalog coverage, generated pages, metadata and local references."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from build_locales import ROOT, LANGUAGES, Translator


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements, self.ids = [], []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        self.elements.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])


def check():
    source = (ROOT / 'src/index.html').read_text()
    catalogs = {lang: json.loads((ROOT / 'locales' / f'{lang}.json').read_text()) for lang in LANGUAGES}
    for lang, meta in LANGUAGES.items():
        catalog = catalogs[lang]
        assert set(catalog) == set(catalogs['en']), f'{lang}: catalog coverage'
        assert all(isinstance(value, str) and value.strip() for value in catalog.values())
        translator = Translator(catalog, lang)
        translator.feed(source)
        expected = ''.join(translator.parts)
        actual = (ROOT / 'public' / lang / 'index.html').read_text()
        assert actual == expected, f'{lang}: generated page is stale'
        page = Page()
        page.feed(actual)
        assert len(page.ids) == len(set(page.ids)), f'{lang}: duplicate IDs'
        assert next(attrs['lang'] for tag, attrs in page.elements if tag == 'html') == meta['tag']
        selected = [a for t, a in page.elements if t == 'a' and a.get('aria-current') == 'page']
        assert len(selected) == 1 and selected[0]['data-language'] == lang
        alternates = [a['hreflang'] for t, a in page.elements if t == 'link' and a.get('rel') == 'alternate']
        assert set(alternates) == {'en', 'pt-BR', 'es', 'x-default'}
        assert len([a for t, a in page.elements if t == 'link' and a.get('rel') == 'canonical']) == 1
        scripts = [a['src'] for t, a in page.elements if t == 'script']
        assert scripts.index(f'/locales/{lang}.js') < scripts.index('/motion.js') < scripts.index('/viewer.js') < scripts.index('/app.js')
        for tag, attrs in page.elements:
            ref = attrs.get('src') if tag == 'script' else attrs.get('href') if tag in ('a', 'link') else None
            if not ref:
                continue
            if ref.startswith('#') and len(ref) > 1:
                assert ref[1:] in page.ids, ref
            if ref.startswith('/'):
                target = ROOT / 'public' / ref.lstrip('/')
                assert target.exists(), ref
        assert catalog['Your agents.'] in actual
        assert catalog['The scale refers to the geometric model. This revision is not yet released for manufacturing.'] in actual
        for filename in ('viewer.js', 'app.js'):
            script = (ROOT / 'public' / filename).read_text()
            for key in re.findall(r'''\bt\(["']([^"']+)["']\)''', script):
                assert key in catalog, f'{lang}: missing dynamic message {key}'
        print(f'{lang}: complete catalog, translated HTML, links and metadata verified')
    assert (ROOT / 'public/index.html').read_bytes() == (ROOT / 'public/en/index.html').read_bytes(), 'Root must be English'
    print('Default route: English. No automatic browser-language override.')


if __name__ == '__main__':
    check()
