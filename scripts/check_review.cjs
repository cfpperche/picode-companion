/* Regressions found during the adversarial review. */
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),zlib=require('node:zlib'),crypto=require('node:crypto');
const read=p=>fs.readFileSync(p,'utf8'),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const raw=JSON.parse(zlib.gunzipSync(Buffer.from(read('public/assets/companion-c04.b64'),'base64'))),catalog=JSON.parse(read('public/catalog.json')),manifest=JSON.parse(read('public/assets/parts/manifest.json'));
assert.equal(manifest.geometry_sha256,hash('public/assets/companion-c04.b64'));
for(const [id,p] of Object.entries(manifest.previews))assert.equal(p.sha256,hash(`public/assets/parts/${id}.svg`));
for(const item of catalog.items)if(item.meshIds.length){assert.deepEqual(manifest.previews[item.id].mesh_ids,item.previewIds);assert.ok(item.previewBoundsMm.every(Number.isFinite));}
const metadata=JSON.parse(read('hardware/components.json')).validation;
assert.equal(metadata.parts,raw.length);assert.equal(metadata.triangles,raw.reduce((n,p)=>n+Buffer.from(p.i,'base64').length/6,0));
const context={};vm.runInNewContext(read('public/view-geometry.js'),context);const g=context.PiCodeViewGeometry;
assert.equal(g.opacity({g:'shutter'},'camera',true,'inside'),1);assert.equal(g.opacity({g:'mute'},'ports',true,'inside'),1);assert.equal(g.opacity({g:'display'},'camera',true,'inside'),0);
const bearing=catalog.items.find(p=>p.id==='MOT-05');assert.deepEqual(bearing.previewBoundsMm,[37,37,7]);
const elements=new Map(),lists={};function element(id){if(!elements.has(id))elements.set(id,{value:'',checked:false,dataset:{},classList:{remove(){},toggle(){}},listeners:{},addEventListener(k,f){(this.listeners[k]||=[]).push(f)},dispatchEvent(e){for(const f of this.listeners[e.type]||[])f(e)},setAttribute(k,v){this[k]=v},scrollIntoView(){},focus(){}});return elements.get(id)}
for(const [attr,values] of Object.entries({mode:['exterior','inside','explode','specs'],component:['all','compute','camera'],panel:['exterior','inside'],finish:[],explore:[]}))lists[`[data-${attr}]`]=values.map(value=>{const el=element(attr+value);el.dataset[attr]=value;return el});
vm.runInNewContext(read('public/app.js'),{window:{addEventListener(){}},document:{documentElement:element('html'),getElementById:element,querySelectorAll:s=>lists[s]||[]},Event:class{constructor(type){this.type=type}},matchMedia:()=>({matches:false})});
element('componentcompute').dispatchEvent({type:'click'});assert.equal(element('pcc-mode').value,'inside');assert.equal(element('modeinside')['aria-pressed'],'true');
element('pcc-isolate').checked=true;element('clear-selection').dispatchEvent({type:'click'});assert.equal(element('pcc-isolate').checked,false);
element('modeexterior').dispatchEvent({type:'click'});element('pcc-isolate').checked=true;element('pcc-isolate').dispatchEvent({type:'change'});assert.equal(element('pcc-component').value,'compute');assert.equal(element('pcc-isolate').checked,true);assert.equal(element('modeinside')['aria-pressed'],'true');
element('modespecs').dispatchEvent({type:'click'});assert.equal(element('pcc-isolate').checked,false);
(async()=>{let requests=0;const loader={window:{},AbortController,setTimeout,clearTimeout,Uint8Array,Blob,Response,DecompressionStream,atob:s=>Buffer.from(s,'base64').toString('binary'),fetch:async()=>{if(++requests===1)throw Error('network');return new Response(read('public/assets/companion-c04.b64'));}};vm.runInNewContext(read('public/model.js'),loader);await assert.rejects(loader.window.PiCodeModel.load());assert.equal((await loader.window.PiCodeModel.load()).length,981);assert.equal(requests,2);console.log('Review regressions passed: preview provenance, metadata, selection, mode state, isolation reset and retry after network failure.');})().catch(e=>{console.error(e);process.exitCode=1});
