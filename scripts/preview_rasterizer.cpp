// Deterministic orthographic z-buffer for model-derived preview assets, not CAD generation.
#include <algorithm>
#include <cmath>
#include <vector>
extern "C" void rasterize(const float* triangles,const unsigned char* colors,int count,int width,int height,unsigned char* pixels){
 std::vector<float> depth(width*height,INFINITY);
 std::fill(pixels,pixels+width*height*4,0);
 for(int t=0;t<count;t++){
  const float* p=triangles+t*9;
  float den=(p[4]-p[7])*(p[0]-p[6])+(p[6]-p[3])*(p[1]-p[7]);
  if(std::abs(den)<1e-8f)continue;
  int left=std::max(0,(int)std::floor(std::min({p[0],p[3],p[6]}))),right=std::min(width-1,(int)std::ceil(std::max({p[0],p[3],p[6]})));
  int top=std::max(0,(int)std::floor(std::min({p[1],p[4],p[7]}))),bottom=std::min(height-1,(int)std::ceil(std::max({p[1],p[4],p[7]})));
  for(int y=top;y<=bottom;y++)for(int x=left;x<=right;x++){
   float a=((p[4]-p[7])*(x+.5f-p[6])+(p[6]-p[3])*(y+.5f-p[7]))/den;
   float b=((p[7]-p[1])*(x+.5f-p[6])+(p[0]-p[6])*(y+.5f-p[7]))/den,c=1-a-b;
   if(a<-.00001f||b<-.00001f||c<-.00001f)continue;
   float z=a*p[2]+b*p[5]+c*p[8];int index=y*width+x;
   if(z>depth[index])continue;
   depth[index]=z;for(int k=0;k<3;k++)pixels[index*4+k]=colors[t*3+k];pixels[index*4+3]=255;
  }
 }
}
