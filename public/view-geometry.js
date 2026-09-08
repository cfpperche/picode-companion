/* Shared, testable rules for component isolation and measured selection bounds. */
((root)=>{
 'use strict';
 const mountOffsets={camera:[-26,-20,43],mic:[-45,0,0],compute:[-45,24,0],display:[0,-55,2]};
 function linked(part,key){
  if(key==='all')return true;
  if(part.g===key)return true;
  if(key==='camera'&&['shutter','shutterrail'].includes(part.g))return true;
  if(key==='ports'&&part.g==='mute')return true;
  if(key==='speaker'&&['acoustic','roof'].includes(part.g))return true;
  if(key==='rotation'&&part.n==='Base / 160 x 182 mm')return true;
  return part.g==='mounts'&&mountOffsets[key]?.every((value,i)=>part.e[i]===value);
 }
 function opacity(part,key,isolate,mode){
  if(isolate&&key!=='all'){
   if(!linked(part,key))return 0;
   if(key==='speaker'&&['acoustic','roof'].includes(part.g))return .15;
   if(key==='rotation'&&part.n==='Base / 160 x 182 mm')return .12;
   return 1;
  }
  if(key==='rotation'&&part.n==='Base / 160 x 182 mm')return .12;
  if(mode!=='inside')return 1;
  if(['shell','bezel','roof','base','deck','keys','shutterrail','shutter','rotation_cover'].includes(part.g))return 0;
  if(part.g==='acoustic')return .15;
  if(part.g==='display'&&/LCD · vidro|Área ativa|Pixels|Expressão/.test(part.n))return .12;
  return 1;
 }
 function bounds(parts,transform=point=>point){
  const low=[Infinity,Infinity,Infinity],high=[-Infinity,-Infinity,-Infinity];
  for(const part of parts)for(const corner of part.corners){const point=transform(corner,part);for(let i=0;i<3;i++){low[i]=Math.min(low[i],point[i]);high[i]=Math.max(high[i],point[i]);}}
  return {low,high,size:high.map((value,i)=>value-low[i])};
 }
 root.PiCodeViewGeometry=Object.freeze({linked,opacity,bounds});
})(typeof window==='undefined'?globalThis:window);
