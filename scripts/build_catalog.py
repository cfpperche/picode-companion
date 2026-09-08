"""Build the BOM/mesh mapping and accessible, server-rendered catalog markup."""
import base64, gzip, hashlib, json, struct
from html import escape as esc
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CATEGORIES=['Enclosure','Electronics','Motion','Mounting','Controls','Connections']
def build_data():
    source=json.loads((ROOT/'hardware/bom.json').read_text())
    asset=(ROOT/'public/assets'/source['geometry']).read_bytes()
    assert hashlib.sha256(asset).hexdigest()==source['geometry_sha256'], 'Geometry changed: review BOM mapping first'
    meshes=json.loads(gzip.decompress(base64.b64decode(asset)))
    def match(selector):
        return [i for i,m in enumerate(meshes) if i in selector.get('indices',[]) or m['n'] in selector.get('names',[]) or m['g'] in selector.get('groups',[]) or any(m['n'].startswith(p) for p in selector.get('prefixes',[]))]
    assigned=[]; items=[]
    for original in source['items']:
        item={k:v for k,v in original.items() if k not in ('selectors','preview')}
        item['meshIds']=match(original['selectors'])
        item['previewIds']=match(original['preview']) if 'preview' in original else item['meshIds']
        assert not original['selectors'] or item['meshIds'],item['id']
        assert set(item['previewIds'])<=set(item['meshIds']),item['id']
        if item['previewIds']:
            points=[point for i in item['previewIds'] for point in struct.iter_unpack('<hhh',base64.b64decode(meshes[i]['p']))]
            item['previewBoundsMm']=[round((max(p[a] for p in points)-min(p[a] for p in points))/100,2) for a in range(3)]
        assigned.extend(item['meshIds']);items.append(item)
    assert len(assigned)==len(set(assigned)), 'A mesh is assigned to multiple BOM entries'
    assert set(assigned)|set(source['excluded_visual_indices'])==set(range(len(meshes))), 'Unmapped geometry'
    data={'revision':source['revision'],'geometry_sha256':source['geometry_sha256'],'items':items}
    (ROOT/'public/catalog.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
    return data

def qty(item):
    return '<span>To specify</span>' if item['quantity'] is None else f'<span>{item["quantity"]}</span> <span>{item["unit"]}</span>'
def markup(data):
    cards=[]; rows=[]
    for item in data['items']:
        id=esc(item['id']);name=esc(item['name']);spec=esc(item['specification']);category=esc(item['category']);status=esc(item['status'])
        has_model=bool(item['meshIds']);action='Inspect in 3D' if has_model else 'View details'
        preview=f'<img data-part-image="{id}" src="/assets/parts/{id}.svg" width="480" height="320" alt="" loading="lazy" decoding="async">' if has_model else '<span class="part-preview-status">3D not modeled</span>'
        cards.append(f'<article class="part-card" data-part="{id}" data-category="{category}"><button class="part-preview" type="button" data-inspect="{id}" aria-label="{name}">{preview}<span class="part-preview-action">{action} <span aria-hidden="true">↗</span></span></button><div class="part-card-copy"><div class="part-meta"><span>{id}</span><span>{qty(item)}</span></div><h3><button type="button" data-inspect="{id}">{name}</button></h3><p>{spec}</p><div class="part-tags"><span>{category}</span><span>{status}</span></div></div></article>')
        rows.append(f'<tr data-part="{id}" data-category="{category}"><td class="part-code">{id}</td><th scope="row"><button type="button" data-inspect="{id}">{name}</button></th><td>{category}</td><td class="part-quantity">{qty(item)}</td><td>{spec}</td><td>{status}</td><td><button class="part-table-action" type="button" data-inspect="{id}">{action}</button></td></tr>')
    options=''.join(f'<option value="{cat}">{cat}</option>' for cat in CATEGORIES)
    return f'''<section id="materiais" class="parts-section" aria-labelledby="parts-title">
<div class="parts-heading"><div><p class="eyebrow">PROJECT CATALOG / C.04</p><h2 id="parts-title">Every part, in its place.</h2><p>Explore the individual parts or check quantities in the bill of materials.</p></div><a class="parts-download" id="bom-download" href="/bom/en.csv" download>Download BOM · CSV <span aria-hidden="true">↓</span></a></div>
<div class="parts-toolbar"><div class="parts-views" role="group" aria-label="Catalog view"><button type="button" data-catalog-view="grid" aria-pressed="true">3D catalog</button><button type="button" data-catalog-view="table" aria-pressed="false">Bill of materials</button></div><label class="part-search"><span>Search parts</span><input id="part-search" type="search" aria-label="Search by name, ID or specification" autocomplete="off"></label><label class="part-category"><span>Category</span><select id="part-category"><option value="all">All categories</option>{options}</select></label></div>
<div class="parts-summary"><p id="parts-count" role="status"><span>{len(data['items'])}</span> <span>items</span></p><p>Representations grouped by physical item; supplier CAD solids are not counted as separate purchases.</p></div>
<div class="parts-grid" id="parts-grid">{''.join(cards)}</div>
<div class="parts-table-wrap" id="parts-table-wrap" tabindex="0" role="region" aria-label="Bill of materials" hidden><table class="parts-table"><caption class="sr-only">Bill of materials</caption><thead><tr><th scope="col">ID</th><th scope="col">Item</th><th scope="col">Category</th><th scope="col">Quantity</th><th scope="col">Specification</th><th scope="col">Definition</th><th scope="col">Part details</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<div class="parts-empty" id="parts-empty" hidden><p>No parts found. Try another name or category.</p><button type="button" id="part-clear">Clear filters</button></div>
<p class="parts-note">Preliminary BOM. Quantities describe this design, including proposed kits; they are not a purchase release. Prices, final materials and tolerances are pending.</p>
</section>
<dialog id="part-dialog" class="part-dialog" aria-labelledby="part-title"><div class="part-dialog-header"><p id="part-id" class="eyebrow"></p><button type="button" id="part-close" aria-label="Close part details">×</button></div><div class="part-dialog-layout"><div class="part-model-column"><div id="part-stage" class="part-stage"><img id="part-static" width="480" height="320" alt="" hidden><canvas id="part-canvas" tabindex="0" role="img" aria-label="Individual 3D view" aria-describedby="part-help"></canvas><p id="part-model-status" role="status" hidden></p></div><div class="part-view-tools" id="part-view-tools"><label><span>Part view</span><select id="part-view"><option value="iso">3/4 view</option><option value="front">Front</option><option value="back">Rear</option><option value="top">Top</option></select></label><div role="group" aria-label="Zoom"><button type="button" id="part-zoom-in" aria-label="Zoom in">+</button><button type="button" id="part-zoom-out" aria-label="Zoom out">−</button><button type="button" id="part-reset" aria-label="Reset part view">↺</button></div></div><label class="part-element-label" id="part-element-label"><span>Model element</span><select id="part-element"></select></label><p id="part-help" class="part-help">Drag or use arrow keys to rotate. Use + and − to zoom; Home resets the view.</p></div><div class="part-dialog-copy"><h2 id="part-title"></h2><p id="part-spec"></p><dl id="part-facts"></dl><p id="part-bounds-note" class="parts-note">Bounds describe the displayed model, not verified manufacturing dimensions.</p><a id="part-source" class="inline-link" target="_blank" rel="noopener noreferrer" hidden>Open reference <span aria-hidden="true">↗</span></a></div></div></dialog>'''

if __name__=='__main__':
    data=build_data();print(f'Catalog: {len(data["items"])} entries; every physical mesh mapped once.')
