/* Exercise the mesh selection/buffer/camera path without a browser or WebGL dependency. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib');
const root=path.join(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const raw=JSON.parse(zlib.gunzipSync(Buffer.from(read('public/assets/companion-c04.b64'),'base64')));
const catalog=JSON.parse(read('public/catalog.json'));
const constants=['VERTEX_SHADER','FRAGMENT_SHADER','COMPILE_STATUS','LINK_STATUS','ARRAY_BUFFER','ELEMENT_ARRAY_BUFFER','STATIC_DRAW','DEPTH_TEST','LEQUAL','CULL_FACE','BLEND','SHORT','BYTE','TRIANGLES','UNSIGNED_SHORT','COLOR_BUFFER_BIT','DEPTH_BUFFER_BIT'];
const gl=Object.fromEntries(constants.map((key,index)=>[key,index+1]));
let draws=0, uploaded=0;
for(const name of ['createProgram','createShader','createBuffer'])gl[name]=()=>({});
for(const name of ['getShaderParameter','getProgramParameter'])gl[name]=()=>true;
gl.getUniformLocation=(_,name)=>name;gl.getAttribLocation=()=>0;
for(const name of ['shaderSource','compileShader','attachShader','deleteShader','linkProgram','deleteBuffer','bindBuffer','viewport','clearColor','clear','useProgram','enable','depthFunc','disable','enableVertexAttribArray','vertexAttribPointer'])gl[name]=()=>{};
gl.bufferData=(_,data)=>{assert.ok(data.length>0);uploaded++;};
for(const name of ['uniformMatrix3fv','uniform3fv','uniform2fv'])gl[name]=(...args)=>assert.ok([...args.at(-1)].every(Number.isFinite),name);
gl.uniform1f=(_,n)=>assert.ok(Number.isFinite(n));gl.drawElements=(_,count)=>{assert.ok(count>0&&count%3===0);draws++;};
const canvas={width:0,height:0,getContext:()=>gl,addEventListener:()=>{}};
const context={window:{},Map,Int16Array,Int8Array,Uint16Array,Uint8Array,Float32Array,atob:s=>Buffer.from(s,'base64').toString('binary')};
vm.runInNewContext(read('public/part-renderer.js'),context);
const renderer=new context.window.PiCodePartRenderer(canvas,raw);
const owners=new Set();
for(const item of catalog.items){
  for(const id of item.meshIds){assert.ok(!owners.has(id),`duplicate physical mesh ${id}`);owners.add(id);}
  if(!item.meshIds.length){assert.equal(item.status,'To specify');continue;}
  const bounds=renderer.setParts(item.previewIds);assert.ok(bounds.every(n=>n>=0&&Number.isFinite(n)),item.id);
  renderer.reset(item);
  for(const [width,height] of [[480,320],[280,280],[760,390]])renderer.render(width,height);
  renderer.yaw=-1.2;renderer.pitch=-1;renderer.render(480,320);
  if(item.id==='MOT-05')assert.deepEqual(Array.from(bounds),[37,37,7],'Bearing preview must show one actual unit without assembly sweep bounds');
  for(const id of item.meshIds){
    const p=raw[id],positions=new Int16Array(Uint8Array.from(Buffer.from(p.p,'base64')).buffer),indices=new Uint16Array(Uint8Array.from(Buffer.from(p.i,'base64')).buffer);
    assert.ok(indices.every(index=>index<positions.length/3),`bad mesh indices ${id}`);
  }
}
assert.equal(catalog.items.length,55);assert.equal(owners.size,raw.length-2);
for(const lang of ['en','pt','es']){
 const translations=JSON.parse(read(`locales/${lang}.json`));
 for(const item of catalog.items)for(const key of ['name','category','specification','status','unit'])assert.ok(translations[item[key]],`${lang}:${item[key]}`);
 const html=read(`public/${lang}/index.html`);
 assert.equal((html.match(/class="part-card"/g)||[]).length,55);
 assert.ok(html.includes(`/bom/${lang}.csv`));assert.equal((read(`public/bom/${lang}.csv`).match(/\r?\n/g)||[]).length,56);
}
(async()=>{
 let fetches=0;
 const loader={window:{},Uint8Array,Blob,Response,DecompressionStream,atob:context.atob,fetch:async()=>{fetches++;return new Response(read('public/assets/companion-c04.b64'));}};
 vm.runInNewContext(read('public/model.js'),loader);
 const first=loader.window.PiCodeModel.load(),second=loader.window.PiCodeModel.load();assert.equal(first,second);
 const loaded=await first;assert.equal(loaded.length,981);assert.equal(fetches,1);
 console.log(`Catalog verified: 55 entries, ${owners.size} physical meshes, ${draws} finite-camera draw calls, three localized HTML/CSV outputs, one shared geometry request.`);
})().catch(error=>{console.error(error);process.exitCode=1;});
