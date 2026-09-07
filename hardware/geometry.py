import math
import numpy as np
import trimesh as tm

def contour(w,d,r,n=12):
    r=min(r,w/2-.0001,d/2-.0001)
    result=[]
    for cx,cy,a in [(w/2-r,-d/2+r,-math.pi/2),(w/2-r,d/2-r,0),(-w/2+r,d/2-r,math.pi/2),(-w/2+r,-d/2+r,math.pi)]:
        for i in range(n):
            t=a+math.pi/2*i/(n-1)
            result.append([cx+r*math.cos(t),cy+r*math.sin(t)])
    return np.array(result)

def loft(profiles, axis='z', center=(0,0,0), n=12):
    # Perfil: coordenada axial, largura, segunda dimensão, raio do contorno.
    rings=[]
    for q,w,d,r in profiles:
        xy=contour(w,d,r,n)
        rings.append(np.c_[xy,np.full(len(xy),q)])
    v=np.vstack(rings); N=len(rings[0]); f=[]
    for k in range(len(rings)-1):
        for i in range(N):
            a=k*N+i;b=k*N+(i+1)%N;c=(k+1)*N+(i+1)%N;e=(k+1)*N+i
            f.extend([[a,b,c],[a,c,e]])
    v=np.vstack([v,[0,0,profiles[0][0]],[0,0,profiles[-1][0]]])
    for i in range(N):
        f.extend([[len(v)-2,(i+1)%N,i],[len(v)-1,(len(rings)-1)*N+i,(len(rings)-1)*N+(i+1)%N]])
    if axis=='y': v=v[:,[0,2,1]]
    v+=np.array(center)
    m=tm.Trimesh(v,f,process=True);m.fix_normals();return m

def rounded(w,d,h,r=5,edge=2,center=(0,0,0),axis='z',n=12):
    edge=min(edge,h/2-.01,r-.01)
    p=[]
    for t in np.linspace(0,math.pi/2,5):
        inset=edge*(1-math.sin(t))
        p.append((-h/2+edge*(1-math.cos(t)),w-2*inset,d-2*inset,max(.1,r-inset)))
    for t in np.linspace(0,math.pi/2,5):
        inset=edge*(1-math.cos(t))
        p.append((h/2-edge+edge*math.sin(t),w-2*inset,d-2*inset,max(.1,r-inset)))
    return loft(p,axis,center,n)

def diff(a,*b):
    return tm.boolean.difference([a,*b],engine='manifold')

def cylinder(radius,height,center,axis='z',segments=24):
    m=tm.creation.cylinder(radius,height,sections=segments)
    if axis=='y':m.apply_transform(tm.transformations.rotation_matrix(math.pi/2,[1,0,0]))
    m.apply_translation(center);return m

def cap_mesh():
    p=[(0,17,17,2),(1,17.3,17.3,2.1),(8.3,14.5,14.5,2.3),(9.2,13.8,13.8,2.4)]
    for scale in [.85,.65,.4,.15]:
        p.append((8.25+.95*scale*scale,13.8*scale,13.8*scale,2.4*scale))
    cap=loft(p,n=8)
    cavity=rounded(12.6,12.6,10,r=1.5,edge=.5,center=(0,0,2),n=8)
    return diff(cap,cavity)

def line(a,b,width,z):
    a=np.array(a);b=np.array(b);d=b-a;l=np.linalg.norm(d);u=d/l;p=np.array([-u[1],u[0]])*width/2
    q=np.array([a+p,b+p,b-p,a-p]);v=np.c_[q,np.full(4,z)]
    return tm.Trimesh(v,[[0,1,2],[0,2,3]],process=False)

def glyph(kind,z):
    parts=[]
    if kind in ['+','-']:
        parts.append(line((-2,0),(2,0),.7,z))
        if kind=='+':parts.append(line((0,-2),(0,2),.7,z))
    elif kind=='m':
        for a,b in [((-2,-1.9),(-2,1.7)),((-2,1.7),(-.2,1.7)),((-.2,1.7),(-.2,-1.9)),((-.2,1.7),(1.7,1.7)),((1.7,1.7),(1.7,-1.9))]:parts.append(line(a,b,.55,z))
    elif kind in ['left','right']:
        s=-1 if kind=='left' else 1
        verts=np.array([[-2.5,0],[-.2,1.8],[-.2,.7],[2.2,.7],[2.2,-.7],[-.2,-.7],[-.2,-1.8]])
        verts[:,0]*=-s
        parts.append(tm.Trimesh(np.c_[verts,np.full(7,z)],[[0,1,2],[0,2,5],[0,5,6],[2,3,4],[2,4,5]],process=False))
    else:
        for i in range(24):
            a=i*2*math.pi/24;b=(i+1)*2*math.pi/24
            parts.append(line((math.cos(a)*1.15,math.sin(a)*1.15),(math.cos(b)*1.15,math.sin(b)*1.15),.45,z))
        for i in range(8):
            a=i*math.pi/4;parts.append(line((math.cos(a)*1.9,math.sin(a)*1.9),(math.cos(a)*2.65,math.sin(a)*2.65),.43,z))
    return tm.util.concatenate(parts)
