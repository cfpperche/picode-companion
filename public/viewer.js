
(async()=>{
const root=document.getElementById('picode-cyber-c');
const $=id=>root.querySelector('#pcc-'+id),canvas=$('canvas'),overlay=$('overlay'),status=$('detail'),loading=$('loading');
const modeSelect=$('mode'),viewSelect=$('view'),component=$('component'),dimensionCheck=$('dims'),shutterButton=$('shutter');
let mode='exterior',yaw=.59,pitch=.33,zoom=.9,explode=0,closed=false,drag=null,scheduled=false,transition=0,finish='graphite';
const views={iso:[.59,.33],front:[0,0],right:[Math.PI/2,.05],left:[-Math.PI/2,.12],back:[Math.PI+.37,.23],top:[0,Math.PI/2]};
const groups={
 all:{label:'Visão geral',info:'Arraste para girar · roda do mouse para aproximar · escala geométrica em mm.'},
 camera:{label:'Câmera',anchor:[0,55,165],e:[-26,-20,43],info:'Camera Module 3 · 25 × 24 × 11,5 mm · autofocus + obturador físico proposto.',url:'https://www.raspberrypi.com/products/camera-module-3/'},
 mic:{label:'4 microfones',anchor:[-60.2,90,149],e:[-45,0,0],info:'Quatro entradas na lateral esquerda · ReSpeaker Ø100 mm instalada inteira na vertical.',url:'https://files.seeedstudio.com/wiki/respeaker_xvf3800_usb/respeaker_xvf3800_2d_mechanical_drawing.pdf'},
 speaker:{label:'Alto-falante',anchor:[0,122,184],e:[0,0,64],info:'Alto-falante Ø40 mm no topo · grade metálica embutida 82 × 72 mm · câmara reservada 78 × 68 × 30 mm.'},
 sensors:{label:'Sensores',anchor:[41,57,161],e:[32,-10,36],info:'ToF VL53L1X em portadora 13 × 18 mm + reserva de 20 × 20 mm para sensor de luz.',url:'https://www.pololu.com/product/3415'},
 compute:{label:'CM5',anchor:[-17,128,99],e:[-45,24,0],info:'CM5 8 GB · 55 × 40 mm; portadora 55 × 41 mm; dissipador e fan 40 mm com volumes reservados.',url:'https://www.waveshare.com/cm5-nano-b.htm'},
 display:{label:'Display',anchor:[0,63,105],e:[0,-55,2],info:'Waveshare HDMI LCD (C) 4″ · 720 × 720 · reserva de montagem 94 × 94 × 22 mm.',url:'https://www.waveshare.com/4inch-hdmi-lcd-c.htm'},
 ports:{label:'I/O + mute',anchor:[25,183,25],e:[0,0,0],info:'USB-C 5 V, USB de serviço e chave de mute · extensões internas e circuito de mute a desenvolver.'}
};
function setDetail(){
 const item=groups[component.value];status.replaceChildren(document.createTextNode(item.info));
 if(item.url){const a=document.createElement('a');a.href=item.url;a.target='_blank';a.rel='noopener noreferrer';a.textContent=' Fabricante';status.appendChild(a);}
}
try{
 const response=await fetch('/assets/companion-c02.b64');
 if(!response.ok)throw Error('Não foi possível carregar o arquivo do modelo.');
 const source=atob((await response.text()).trim()),compressed=Uint8Array.from(source,c=>c.charCodeAt(0));
 const stream=new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip'));
 const raw=JSON.parse(await new Response(stream).text());
 const gl=canvas.getContext('webgl',{alpha:true,antialias:true,premultipliedAlpha:false});
 if(!gl)throw Error('WebGL indisponível');
 function program(vs,fs){const p=gl.createProgram();for(const [t,s] of [[gl.VERTEX_SHADER,vs],[gl.FRAGMENT_SHADER,fs]]){const sh=gl.createShader(t);gl.shaderSource(sh,s);gl.compileShader(sh);if(!gl.getShaderParameter(sh,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(sh));gl.attachShader(p,sh);}gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));return p;}
 const prog=program(`attribute vec3 aPosition;attribute vec3 aNormal;uniform mat3 uRotation;uniform vec3 uCenter;uniform vec2 uScale;uniform float uDepth;uniform vec3 uOffset;varying vec3 vNormal;
 void main(){vec3 q=uRotation*(aPosition/100.0+uOffset)-uCenter;gl_Position=vec4(q.x*uScale.x,-q.y*uScale.y,q.z/uDepth,1.0);vNormal=aNormal;}`,
 `precision highp float;varying vec3 vNormal;uniform vec3 uColor;uniform vec3 uEye;uniform float uMetal;uniform float uRough;uniform float uEmit;uniform float uAlpha;uniform float uSelect;
 void main(){vec3 n=normalize(vNormal);if(dot(n,uEye)<0.0)n=-n;vec3 l=normalize(vec3(-.48,-.7,1.1));vec3 h=normalize(l+uEye);
 float diffuse=max(0.0,dot(n,l));float spec=pow(max(0.0,dot(n,h)),12.0+160.0*pow(1.0-uRough,2.0));float rim=pow(1.0-abs(dot(n,uEye)),3.0);
 vec3 c=uColor*(.48+.75*diffuse);c+=(.13+.7*uMetal)*spec*mix(vec3(1.0),uColor,uMetal*.5);
 c+=rim*.045*mix(vec3(.0,.8,1.),vec3(1.,.02,.35),max(0.,n.x));
 if(uEmit>0.0)c=mix(c,uColor*1.1,min(1.,uEmit));c+=uSelect*.05*vec3(.0,.85,.8);
 gl_FragColor=vec4(pow(clamp(c,0.0,1.0),vec3(1.0/2.2)),uAlpha);}`);
 const U={};for(const n of ['Rotation','Center','Scale','Depth','Offset','Color','Eye','Metal','Rough','Emit','Alpha','Select'])U[n]=gl.getUniformLocation(prog,'u'+n);
 const aPos=gl.getAttribLocation(prog,'aPosition'),aNorm=gl.getAttribLocation(prog,'aNormal');
 function decode(s,T){const a=Uint8Array.from(atob(s),c=>c.charCodeAt(0));return new T(a.buffer);}
 function buffer(data,target=gl.ARRAY_BUFFER){const b=gl.createBuffer();gl.bindBuffer(target,b);gl.bufferData(target,data,gl.STATIC_DRAW);return b;}
 const parts=raw.map(p=>{const pos=decode(p.p,Int16Array),norm=decode(p.v,Int8Array),idx=decode(p.i,Uint16Array);const min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];for(let i=0;i<pos.length;i++){const a=i%3;min[a]=Math.min(min[a],pos[i]/100);max[a]=Math.max(max[a],pos[i]/100);}const corners=[];for(const x of [min[0],max[0]])for(const y of [min[1],max[1]])for(const z of [min[2],max[2]])corners.push([x,y,z]);return {...p,pos:buffer(pos),norm:buffer(norm),idx:buffer(idx,gl.ELEMENT_ARRAY_BUFFER),count:idx.length,corners,color:p.c.map(c=>Math.pow(c/255,2.2))};});
 const floorProg=program(`attribute vec3 aPosition;uniform mat3 uRotation;uniform vec3 uCenter;uniform vec2 uScale;uniform float uDepth;varying vec2 vFloor;void main(){vec3 q=uRotation*aPosition-uCenter;gl_Position=vec4(q.x*uScale.x,-q.y*uScale.y,q.z/uDepth,1.0);vFloor=aPosition.xy;}`,
 `precision mediump float;varying vec2 vFloor;void main(){vec2 p=(vFloor-vec2(0.,98.))/vec2(67.,90.);float a=exp(-dot(p,p)*2.5)*.19;gl_FragColor=vec4(.025,.03,.04,a);}`);
 const FU={};for(const n of ['Rotation','Center','Scale','Depth'])FU[n]=gl.getUniformLocation(floorProg,'u'+n);
 const fp=gl.getAttribLocation(floorProg,'aPosition'),fb=buffer(new Float32Array([-140,-80,-.5,140,-80,-.5,140,250,-.5,-140,-80,-.5,140,250,-.5,-140,250,-.5]));
 let projectPoint;
 const ns='http://www.w3.org/2000/svg';
 function svg(type,attrs,text){const e=document.createElementNS(ns,type);for(const [k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text)e.textContent=text;overlay.appendChild(e);return e;}
 function annotations(W,H){
  overlay.setAttribute('viewBox',`0 0 ${W} ${H}`);overlay.replaceChildren();
  if(dimensionCheck.checked&&mode!=='explode'){
   const dims=[{a:[-64.5,-12,0],b:[64.5,-12,0],s:'129 mm',o:[0,16]},{a:[78,0,0],b:[78,0,184],s:'184 mm',o:[24,0]},{a:[-77,0,0],b:[-77,184,0],s:'184 mm',o:[-16,0]}];
   for(const d of dims){const a=projectPoint(d.a),b=projectPoint(d.b);if(Math.hypot(a[0]-b[0],a[1]-b[1])<40)continue;svg('line',{x1:a[0],y1:a[1],x2:b[0],y2:b[1]});for(const p of [a,b])svg('line',{x1:p[0]-3,y1:p[1]-3,x2:p[0]+3,y2:p[1]+3});const x=Math.max(31,Math.min(W-31,(a[0]+b[0])/2+d.o[0])),y=Math.max(16,Math.min(H-9,(a[1]+b[1])/2+d.o[1]));svg('rect',{x:x-27,y:y-12,width:54,height:17,rx:3});svg('text',{x,y,'text-anchor':'middle'},d.s);}
  }
  const item=groups[component.value];if(item.anchor){const a=projectPoint(item.anchor.map((v,i)=>v+item.e[i]*explode)),x=Math.max(65,Math.min(W-65,a[0]+(a[0]>W/2?58:-58))),y=Math.max(22,Math.min(H-12,a[1]-39));svg('line',{x1:a[0],y1:a[1],x2:x,y2:y+6});svg('circle',{cx:a[0],cy:a[1],r:4,fill:'var(--background)',stroke:'var(--foreground)','stroke-width':1.5});svg('rect',{x:x-59,y:y-13,width:118,height:21,rx:3});svg('text',{x,y,'text-anchor':'middle'},item.label);}
 }
 function offset(p){return p.e.map((n,i)=>n*explode+(p.g==='shutter'&&i===0&&closed?-18:0));}
 function opacity(p){if(mode!=='inside')return 1;if(['shell','bezel','roof','base','deck','keys','shutterrail','shutter'].includes(p.g))return 0;if(p.g==='display')return .12;return 1;}
 function materialColor(p){
  if(finish==='graphite')return p.color;
  const convertible=['base','deck','shell'];
  const shell=convertible.includes(p.g)&&!p.l&&p.m<.5&&!/borracha|rubber|parafuso|screw|pé|foot/i.test(p.n);
  const key=p.g==='keys'&&!p.l&&p.m<.5&&/keycap|tecla/i.test(p.n);
  if(shell||key){const rgb=finish==='pearl'?(key?[.91,.92,.93]:[.79,.81,.84]):(key?[.98,.91,.93]:[.84,.49,.64]);return rgb.map(c=>Math.pow(c,2.2));}
  return p.color;
 }
 function draw(){
  scheduled=false;const b=canvas.parentElement.getBoundingClientRect(),W=Math.max(1,b.width),H=Math.max(1,b.height),dpr=Math.min(devicePixelRatio||1,2);
  if(canvas.width!==Math.round(W*dpr)||canvas.height!==Math.round(H*dpr)){canvas.width=Math.round(W*dpr);canvas.height=Math.round(H*dpr);}
  gl.viewport(0,0,canvas.width,canvas.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
  const cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch),rot=new Float32Array([cy,sy*sp,-sy*cp,sy,-cy*sp,cy*cp,0,-cp,-sp]);
  const eye=[sy*cp,-cy*cp,sp],lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];
  function project(p){const[x,y,z]=p;return[cy*x+sy*y,sy*sp*x-cy*sp*y-cp*z,-sy*cp*x+cy*cp*y-sp*z];}
  for(const p of parts)for(const c of p.corners){const off=offset(p),q=project(c.map((v,i)=>v+off[i]));for(let i=0;i<3;i++){lo[i]=Math.min(lo[i],q[i]);hi[i]=Math.max(hi[i],q[i]);}}
  const center=lo.map((v,i)=>(v+hi[i])/2),margin=dimensionCheck.checked?94:40,s=Math.min((W-margin)/(hi[0]-lo[0]),(H-margin)/(hi[1]-lo[1]))*zoom,scale=[2*s/W,2*s/H],depth=(hi[2]-lo[2])/2+250;
  projectPoint=p=>{const q=project(p);return[(q[0]-center[0])*s+W/2,(q[1]-center[1])*s+H/2];};
  function camera(u){gl.uniformMatrix3fv(u.Rotation,false,rot);gl.uniform3fv(u.Center,center);gl.uniform2fv(u.Scale,scale);gl.uniform1f(u.Depth,depth);}
  gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.disable(gl.DEPTH_TEST);gl.depthMask(false);gl.useProgram(floorProg);camera(FU);gl.bindBuffer(gl.ARRAY_BUFFER,fb);gl.enableVertexAttribArray(fp);gl.vertexAttribPointer(fp,3,gl.FLOAT,false,0,0);gl.drawArrays(gl.TRIANGLES,0,6);gl.disableVertexAttribArray(fp);
  gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);gl.disable(gl.CULL_FACE);gl.useProgram(prog);camera(U);gl.uniform3fv(U.Eye,eye);gl.enableVertexAttribArray(aPos);gl.enableVertexAttribArray(aNorm);
  for(const pass of [1,0]){gl.depthMask(pass===1);for(const p of parts){const alpha=opacity(p);if(alpha===0||(pass===1)!==(alpha===1))continue;gl.bindBuffer(gl.ARRAY_BUFFER,p.pos);gl.vertexAttribPointer(aPos,3,gl.SHORT,false,0,0);gl.bindBuffer(gl.ARRAY_BUFFER,p.norm);gl.vertexAttribPointer(aNorm,3,gl.BYTE,true,0,0);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,p.idx);gl.uniform3fv(U.Offset,offset(p));gl.uniform3fv(U.Color,materialColor(p));gl.uniform1f(U.Metal,p.m);gl.uniform1f(U.Rough,p.r);gl.uniform1f(U.Emit,p.l);gl.uniform1f(U.Alpha,alpha);gl.uniform1f(U.Select,component.value===p.g?1:0);gl.drawElements(gl.TRIANGLES,p.count,gl.UNSIGNED_SHORT,0);}}
  gl.depthMask(true);gl.disableVertexAttribArray(aPos);gl.disableVertexAttribArray(aNorm);annotations(W,H);
 }
 function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
 function changeMode(){mode=modeSelect.value;zoom=.9;cancelAnimationFrame(transition);const start=explode,end=mode==='explode'?1:0,t0=performance.now();if(matchMedia('(prefers-reduced-motion: reduce)').matches){explode=end;requestDraw();return;}function tick(t){const f=Math.min((t-t0)/300,1);explode=start+(end-start)*f*f*(3-2*f);requestDraw();if(f<1)transition=requestAnimationFrame(tick);}transition=requestAnimationFrame(tick);}
 modeSelect.addEventListener('change',changeMode);
 viewSelect.addEventListener('change',()=>{[yaw,pitch]=views[viewSelect.value];zoom=.9;requestDraw();});
 component.addEventListener('change',()=>{const k=component.value;if(k==='mic'){[yaw,pitch]=[-1.13,.25];viewSelect.value='left';}else if(k==='speaker'){[yaw,pitch]=[.45,1.02];viewSelect.value='top';}else if(k==='compute'){modeSelect.value='inside';changeMode();[yaw,pitch]=[.65,.5];viewSelect.value='iso';}else if(k==='ports'){[yaw,pitch]=views.back;viewSelect.value='back';}else if(k!=='all'){[yaw,pitch]=[.12,.17];viewSelect.value='front';}zoom=.9;setDetail();requestDraw();});
 dimensionCheck.addEventListener('change',()=>{zoom=.9;requestDraw();});
 shutterButton.addEventListener('click',()=>{closed=!closed;shutterButton.setAttribute('aria-pressed',String(closed));shutterButton.textContent=closed?'Abrir obturador':'Fechar obturador';component.value='camera';setDetail();status.appendChild(document.createTextNode(closed?' Obturador fechado na simulação.':' Obturador aberto na simulação.'));requestDraw();});
 canvas.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY,yaw,pitch};canvas.setPointerCapture(e.pointerId);});
 canvas.addEventListener('pointermove',e=>{if(!drag)return;yaw=drag.yaw+(e.clientX-drag.x)*.009;pitch=Math.max(-1.4,Math.min(1.57,drag.pitch-(e.clientY-drag.y)*.008));requestDraw();});
 canvas.addEventListener('lostpointercapture',()=>drag=null);canvas.addEventListener('pointerup',()=>drag=null);canvas.addEventListener('pointercancel',()=>drag=null);
 canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.65,Math.min(1.8,zoom*Math.exp(-e.deltaY*.001)));requestDraw();},{passive:false});
 canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();loading.hidden=false;loading.textContent='Visualização 3D interrompida. Reabra esta visualização.';});
 window.PiCodeViewer={
  setFinish(value){finish=value;requestDraw();},
  setExplosion(value){cancelAnimationFrame(transition);explode=Math.max(0,Math.min(1,value));requestDraw();},
  zoomBy(factor){zoom=Math.max(.65,Math.min(1.8,zoom*factor));requestDraw();},
  reset(){[yaw,pitch]=views.iso;viewSelect.value='iso';zoom=.9;requestDraw();},
  select(key){component.value=key;component.dispatchEvent(new Event('change'));},
  state(){return{mode,yaw,pitch,zoom,explode,closed,finish,component:component.value};}
 };
 canvas.addEventListener('keydown',e=>{
  if(e.key==='ArrowLeft')yaw-=.15;
  else if(e.key==='ArrowRight')yaw+=.15;
  else if(e.key==='ArrowUp')pitch=Math.min(1.57,pitch+.12);
  else if(e.key==='ArrowDown')pitch=Math.max(-1.4,pitch-.12);
  else if(e.key==='+'||e.key==='=')window.PiCodeViewer.zoomBy(1.1);
  else if(e.key==='-')window.PiCodeViewer.zoomBy(1/1.1);
  else if(e.key==='Home')window.PiCodeViewer.reset();
  else return;
  e.preventDefault();requestDraw();
 });
 loading.hidden=true;draw();new ResizeObserver(requestDraw).observe(canvas.parentElement);root.dataset.ready='true';
 window.dispatchEvent(new Event('picode-ready'));
}catch(e){loading.textContent='Não foi possível iniciar o 3D neste navegador.';status.textContent=e.message;root.dataset.error=e.message;}
})();
