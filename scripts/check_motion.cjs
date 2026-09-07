const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
require('../public/motion.js');
const m = globalThis.PiCodeMotion;
const near = (a,b) => assert.ok(Math.abs(a-b)<1e-8, `${a} != ${b}`);
for (const [head,servo] of [[-180,30],[-90,90],[0,150],[90,210],[180,270]]) near(m.servoDegrees(head),servo);
assert.equal(m.clamp(999),180); assert.equal(m.clamp(-999),-180);
assert.throws(()=>m.clamp(NaN)); assert.throws(()=>m.clamp(Infinity));
// No modulo/shortest-path collapse between the mechanically distinct endpoints.
assert.equal(m.servoDegrees(180)-m.servoDegrees(-180),240);
const front=[0,58,165], fixed=[36,16,41];
for(let a=-180;a<=180;a+=5){
  assert.deepEqual(m.transform(fixed,'fixed',a),fixed);
  const p=m.transform(front,'head',a);
  near(Math.hypot(p[0],p[1]-118),60); near(p[2],165);
  const back=m.transform(p,'head',-a);back.forEach((v,i)=>near(v,front[i]));
  const drive=m.transform([m.driveX+10,118,53],'drive',a);
  near(Math.atan2(drive[1]-118,drive[0]-m.driveX)*180/Math.PI,a/1.5);
  assert.deepEqual(m.transform([4,118,42],'flex',a),[4,118,42]);
  m.transform([16,128,97],'flex',a).forEach((v,i)=>near(v,m.transform([16,128,97],'head',a)[i]));
}
near(m.transform(front,'head',-90)[0],-60);
const root=path.join(__dirname,'..');
const parts=JSON.parse(zlib.gunzipSync(Buffer.from(fs.readFileSync(path.join(root,'public/assets/companion-c04.b64'),'utf8'),'base64')));
assert.equal(parts.filter(p=>p.n.startsWith('ReSpeaker supplier CAD')).length,580);
for(const p of parts){
  assert.ok(['fixed','head','drive','flex'].includes(p.j),p.n);
  if(['keys','base','ports','mute','deck'].includes(p.g))assert.equal(p.j,'fixed',p.n);
  if(['camera','mic','compute','display','speaker','shell','bezel','roof','mounts','acoustic'].includes(p.g))assert.equal(p.j,'head',p.n);
  assert.ok(Buffer.from(p.p,'base64').length>0);
}
assert.equal(parts.filter(p=>p.n.startsWith('6805 bearing')).length,2);
assert.equal(parts.filter(p=>p.n.startsWith('Drive pulley tooth')).length,72);
assert.equal(parts.filter(p=>p.n.startsWith('Output pulley tooth')).length,48);
const report=JSON.parse(fs.readFileSync(path.join(root,'hardware/verificacao.json'),'utf8'));
near(Number((-m.driveX).toFixed(4)),report.rotation.pulley_center_distance_mm);
assert.equal(parts.length,report.parts);
console.log('C.04: ±180° travel, 3:2 transmission, fixed base, rigid head, flex endpoints and model metadata verified.');
