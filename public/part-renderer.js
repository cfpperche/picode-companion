/* Native WebGL part renderer. Fits actual selected geometry, independent of head travel. */
(() => {
  'use strict';
  const decoded = new Map();
  function decode(text, Type) {
    return new Type(Uint8Array.from(atob(text), c => c.charCodeAt(0)).buffer);
  }
  window.PiCodePartRenderer = class {
    constructor(canvas, raw) {
      this.canvas = canvas; this.raw = raw; this.parts = []; this.zoom = 1;
      this.yaw = .5; this.pitch = .45; this.lost = false;
      const gl = this.gl = canvas.getContext('webgl', {alpha: true, antialias: true, premultipliedAlpha: false});
      if (!gl) throw Error('WebGL is unavailable');
      const vs = `attribute vec3 aPosition;attribute vec3 aNormal;uniform mat3 uRotation;uniform vec3 uCenter;uniform vec2 uScale;uniform float uDepth;varying vec3 vNormal;
        void main(){vec3 q=uRotation*(aPosition/100.0)-uCenter;gl_Position=vec4(q.x*uScale.x,-q.y*uScale.y,q.z/uDepth,1.0);vNormal=aNormal;}`;
      const fs = `precision highp float;varying vec3 vNormal;uniform vec3 uColor;uniform vec3 uEye;uniform float uMetal;uniform float uRough;uniform float uEmit;
        void main(){vec3 n=normalize(vNormal);if(dot(n,uEye)<0.0)n=-n;vec3 l=normalize(vec3(-.48,-.7,1.1));vec3 h=normalize(l+uEye);float d=max(0.0,dot(n,l));float s=pow(max(0.0,dot(n,h)),12.0+160.0*pow(1.0-uRough,2.0));vec3 c=uColor*(.48+.75*d);c+=(.13+.7*uMetal)*s*mix(vec3(1.0),uColor,uMetal*.5);if(uEmit>0.0)c=mix(c,uColor*1.1,min(1.0,uEmit));gl_FragColor=vec4(pow(clamp(c,0.0,1.0),vec3(1.0/2.2)),1.0);}`;
      const program = this.program = gl.createProgram();
      for (const [type, code] of [[gl.VERTEX_SHADER, vs], [gl.FRAGMENT_SHADER, fs]]) {
        const shader = gl.createShader(type); gl.shaderSource(shader, code); gl.compileShader(shader);
        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw Error('Shader compilation failed');
        gl.attachShader(program, shader); gl.deleteShader(shader);
      }
      gl.linkProgram(program);
      if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw Error('Shader linking failed');
      this.uniforms = Object.fromEntries(['Rotation','Center','Scale','Depth','Color','Eye','Metal','Rough','Emit'].map(n => [n, gl.getUniformLocation(program, 'u' + n)]));
      this.position = gl.getAttribLocation(program, 'aPosition'); this.normal = gl.getAttribLocation(program, 'aNormal');
      canvas.addEventListener('webglcontextlost', event => {event.preventDefault(); this.lost = true; canvas.dispatchEvent(new Event('part-context-lost'));});
    }
    setParts(ids) {
      const gl = this.gl;
      for (const p of this.parts) for (const key of ['position','normal','index']) gl.deleteBuffer(p[key]);
      this.parts = [];
      const low = [Infinity,Infinity,Infinity], high = [-Infinity,-Infinity,-Infinity];
      for (const id of ids) {
        const source = this.raw[id];
        if (!source) throw Error('Unknown part');
        if (!decoded.has(id)) {
          const position = decode(source.p, Int16Array), normal = decode(source.v, Int8Array), index = decode(source.i, Uint16Array);
          const min = [Infinity,Infinity,Infinity], max = [-Infinity,-Infinity,-Infinity];
          for (let i = 0; i < position.length; i++) {const axis = i % 3; min[axis] = Math.min(min[axis], position[i]/100); max[axis] = Math.max(max[axis], position[i]/100);}
          decoded.set(id, {position,normal,index,min,max});
        }
        const d = decoded.get(id), part = {source, count:d.index.length};
        for (const key of ['position','normal','index']) {
          const target = key === 'index' ? gl.ELEMENT_ARRAY_BUFFER : gl.ARRAY_BUFFER;
          part[key] = gl.createBuffer(); gl.bindBuffer(target, part[key]); gl.bufferData(target, d[key], gl.STATIC_DRAW);
        }
        for (let axis = 0; axis < 3; axis++) {low[axis] = Math.min(low[axis], d.min[axis]); high[axis] = Math.max(high[axis], d.max[axis]);}
        this.parts.push(part);
      }
      this.bounds = {low,high};
      this.corners = [];
      for (const x of [low[0],high[0]]) for (const y of [low[1],high[1]]) for (const z of [low[2],high[2]]) this.corners.push([x,y,z]);
      return high.map((v,i) => v-low[i]);
    }
    reset(item) {
      [this.yaw,this.pitch] = item?.id === 'ELE-05' ? [-1.12,.2] : /^(ELE-0[1278]|ELE-10|MOT-|MNT-)/.test(item?.id || '') ? [.5,.95] : [.5,.4];
      this.zoom = 1;
    }
    render(width, height, dpr = 1) {
      if (this.lost) throw Error('WebGL context lost');
      if (!this.parts.length) return;
      const gl = this.gl, u = this.uniforms, W = Math.max(1,width), H = Math.max(1,height);
      const pixelW = Math.round(W*dpr), pixelH = Math.round(H*dpr);
      if (this.canvas.width !== pixelW || this.canvas.height !== pixelH) {this.canvas.width=pixelW;this.canvas.height=pixelH;}
      gl.viewport(0,0,pixelW,pixelH);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
      const cy=Math.cos(this.yaw),sy=Math.sin(this.yaw),cp=Math.cos(this.pitch),sp=Math.sin(this.pitch);
      const rot=new Float32Array([cy,sy*sp,-sy*cp,sy,-cy*sp,cy*cp,0,-cp,-sp]);
      const lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];
      for (const [x,y,z] of this.corners) {
        const q=[cy*x+sy*y,sy*sp*x-cy*sp*y-cp*z,-sy*cp*x+cy*cp*y-sp*z];
        for(let i=0;i<3;i++){lo[i]=Math.min(lo[i],q[i]);hi[i]=Math.max(hi[i],q[i]);}
      }
      const center=lo.map((v,i)=>(v+hi[i])/2),s=Math.min(W*.78/Math.max(.01,hi[0]-lo[0]),H*.76/Math.max(.01,hi[1]-lo[1]))*this.zoom;
      gl.useProgram(this.program);gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);gl.disable(gl.CULL_FACE);gl.disable(gl.BLEND);
      gl.uniformMatrix3fv(u.Rotation,false,rot);gl.uniform3fv(u.Center,center);gl.uniform2fv(u.Scale,[2*s/W,2*s/H]);gl.uniform1f(u.Depth,(hi[2]-lo[2])/2+100);
      gl.uniform3fv(u.Eye,[sy*cp,-cy*cp,sp]);gl.enableVertexAttribArray(this.position);gl.enableVertexAttribArray(this.normal);
      for(const p of this.parts){
        gl.bindBuffer(gl.ARRAY_BUFFER,p.position);gl.vertexAttribPointer(this.position,3,gl.SHORT,false,0,0);
        gl.bindBuffer(gl.ARRAY_BUFFER,p.normal);gl.vertexAttribPointer(this.normal,3,gl.BYTE,true,0,0);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,p.index);
        gl.uniform3fv(u.Color,p.source.c.map(c=>Math.pow(c/255,2.2)));gl.uniform1f(u.Metal,p.source.m);gl.uniform1f(u.Rough,p.source.r);gl.uniform1f(u.Emit,p.source.l);
        gl.drawElements(gl.TRIANGLES,p.count,gl.UNSIGNED_SHORT,0);
      }
    }
  };
})();
