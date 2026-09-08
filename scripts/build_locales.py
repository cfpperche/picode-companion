#!/usr/bin/env python3
"""Build fully translated static pages. No third-party dependencies required."""
from html import escape
from html.parser import HTMLParser
import json
import csv
from build_catalog import build_data, markup
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://picode-companion-c02.vercel.app'
LANGUAGES = {
    'en': {'tag': 'en', 'og': 'en_US', 'path': '/en/'},
    'pt': {'tag': 'pt-BR', 'og': 'pt_BR', 'path': '/pt/'},
    'es': {'tag': 'es', 'og': 'es_ES', 'path': '/es/'},
}


class Translator(HTMLParser):
    def __init__(self, catalog, language):
        super().__init__(convert_charrefs=True)
        self.catalog, self.language, self.parts = catalog, language, []
        self.meta = LANGUAGES[language]

    def translate(self, value):
        key = value.strip()
        if not key:
            return value
        if key not in self.catalog:
            raise ValueError(f'Missing {self.language} translation: {key!r}')
        start = len(value) - len(value.lstrip())
        end = len(value.rstrip())
        return value[:start] + self.catalog[key] + value[end:]

    def handle_decl(self, declaration):
        self.parts.append(f'<!{declaration}>')

    def handle_comment(self, text):
        self.parts.append(f'<!--{text}-->')

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        for name in ('aria-label', 'title', 'data-nojs'):
            if name in attrs:
                attrs[name] = self.translate(attrs[name])
        if tag == 'meta' and (attrs.get('name') == 'description' or attrs.get('property') in ('og:title', 'og:description')):
            attrs['content'] = self.translate(attrs['content'])
        if tag == 'html':
            attrs['lang'] = self.meta['tag']
        if tag == 'a' and attrs.get('id') == 'bom-download':
            attrs['href'] = f'/bom/{self.language}.csv'
        if tag == 'a' and attrs.get('href') == '/':
            attrs['href'] = self.meta['path']
        if tag == 'a' and attrs.get('data-language') == self.language:
            attrs['aria-current'] = 'page'
        if tag == 'script' and attrs.get('src') == '/locales/runtime.js':
            attrs['src'] = f'/locales/{self.language}.js'
        self.parts.append('<' + tag + ''.join(' ' + k if v is None else f' {k}="{escape(v, quote=True)}"' for k, v in attrs.items()) + '>')

    def handle_endtag(self, tag):
        if tag == 'head':
            self.parts.append(f'<link rel="canonical" href="{ORIGIN}{self.meta["path"]}">')
            self.parts.append(f'<meta property="og:url" content="{ORIGIN}{self.meta["path"]}">')
            self.parts.append(f'<meta property="og:locale" content="{self.meta["og"]}">')
            for language, meta in LANGUAGES.items():
                self.parts.append(f'<link rel="alternate" hreflang="{meta["tag"]}" href="{ORIGIN}{meta["path"]}">')
                if language != self.language:
                    self.parts.append(f'<meta property="og:locale:alternate" content="{meta["og"]}">')
            self.parts.append(f'<link rel="alternate" hreflang="x-default" href="{ORIGIN}/en/">')
        self.parts.append(f'</{tag}>')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.parts[-1] = self.parts[-1][:-1] + '/>'

    def handle_data(self, data):
        self.parts.append(escape(self.translate(data), quote=False))


def read_template():
    return (ROOT / "src/index.html").read_text().replace("<!-- PARTS_CATALOG -->", markup(json.loads((ROOT / "public/catalog.json").read_text())))

def build():
    data = build_data()
    catalogs = {language: json.loads((ROOT / 'locales' / f'{language}.json').read_text()) for language in LANGUAGES}
    keys = set(catalogs['en'])
    for language, catalog in catalogs.items():
        if set(catalog) != keys or any(not isinstance(v, str) or not v.strip() for v in catalog.values()):
            raise ValueError(f'Incomplete translation catalog: {language}')
    template = read_template()
    for language, catalog in catalogs.items():
        csv_dir=ROOT / 'public/bom';csv_dir.mkdir(exist_ok=True)
        with (csv_dir / f'{language}.csv').open('w',encoding='utf-8-sig',newline='') as output:
            writer=csv.writer(output)
            writer.writerow([catalog.get(k,k) for k in ['ID','Item','Category','Quantity','Unit','Specification','Definition','Reference']])
            for item in data['items']:
                writer.writerow([item['id'],catalog[item['name']],catalog[item['category']],item['quantity'] if item['quantity'] is not None else catalog['To specify'],catalog[item['unit']],catalog[item['specification']],catalog[item['status']],item.get('source','')])
        translator = Translator(catalog, language)
        translator.feed(template)
        translator.close()
        rendered = ''.join(translator.parts)
        target = ROOT / 'public' / language / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered)
        if language == 'en':
            (ROOT / 'public' / 'index.html').write_text(rendered)
        runtime = ROOT / 'public' / 'locales' / f'{language}.js'
        runtime.parent.mkdir(exist_ok=True)
        runtime.write_text('"use strict";\nwindow.PiCodeI18n = Object.freeze({\n  locale: ' + json.dumps(LANGUAGES[language]['tag']) + ',\n  messages: Object.freeze(' + json.dumps(catalog, ensure_ascii=False) + '),\n  t(message) { return this.messages[message] ?? message; }\n});\n')
    urls = ''.join(f'<url><loc>{ORIGIN}{meta["path"]}</loc></url>' for meta in LANGUAGES.values())
    (ROOT / 'public' / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + '</urlset>\n')
    (ROOT / 'public' / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n')
    print(f'Built 3 locales + English root; {len(keys)} messages per locale.')


if __name__ == '__main__':
    build()
