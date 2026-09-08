(() => {
  'use strict';
  const t = value => window.PiCodeI18n?.t(value) ?? value;
  const $ = id => document.getElementById(id);
  const section = $('materiais'), dialog = $('part-dialog'), canvas = $('part-canvas');
  const cards = [...section.querySelectorAll('.part-card')];
  let dataPromise, modelPromise, renderer, current, lastTrigger, raw, drag, frame, requestId = 0;
  const data = () => dataPromise ||= fetch('/catalog.json').then(response => {if (!response.ok) throw Error('Catalog unavailable'); return response.json();});
  const model = () => modelPromise ||= window.PiCodeModel.load().then(value => (raw = value)).catch(error=>{modelPromise=undefined;throw error;});
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  const searchText = new Map(cards.map(card => [card.dataset.part,normalize(card.textContent)]));
  function filter() {
    const query=normalize($('part-search').value.trim()), category=$('part-category').value;
    const ids = new Set(cards.filter(card => (category==='all'||category===card.dataset.category)&&searchText.get(card.dataset.part).includes(query)).map(card => card.dataset.part));
    section.querySelectorAll('[data-part]').forEach(element => {element.hidden=!ids.has(element.dataset.part);});
    $('parts-count').textContent = `${ids.size} ${t('of')} ${cards.length} ${t('items')}`;
    $('parts-empty').hidden=ids.size>0;
  }
  $('part-search').addEventListener('input',filter);$('part-category').addEventListener('change',filter);
  $('part-clear').addEventListener('click',()=>{$('part-search').value='';$('part-category').value='all';filter();$('part-search').focus();});
  section.querySelectorAll('[data-catalog-view]').forEach(button => button.addEventListener('click',()=>{
    const grid=button.dataset.catalogView==='grid';$('parts-grid').hidden=!grid;$('parts-table-wrap').hidden=grid;
    section.querySelectorAll('[data-catalog-view]').forEach(other => other.setAttribute('aria-pressed',String(other===button)));
  }));
  const fact=(label,value)=>{const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=t(label);dd.textContent=value;$('part-facts').append(dt,dd);return dd;};
  function showModelError(message) {
    canvas.hidden=true;if(current?.meshIds?.length){$('part-static').hidden=false;message='Static model preview. Interactive 3D is unavailable in this browser.';}$('part-model-status').textContent=t(message);$('part-model-status').hidden=false;
    $('part-view-tools').hidden=true;$('part-element-label').hidden=true;$('part-help').hidden=true;$('part-bounds-note').hidden=!current?.previewBoundsMm;
  }
  function draw() {
    frame=0;if(!dialog.open||!renderer||canvas.hidden)return;
    try {const rect=$('part-stage').getBoundingClientRect();renderer.render(rect.width,rect.height,Math.min(window.devicePixelRatio||1,2));}
    catch {showModelError('Part geometry is unavailable. Material details remain below.');}
  }
  function schedule(){if(!frame)frame=requestAnimationFrame(draw);}
  function selectGeometry() {
    if(!renderer||!current)return;
    const selection=$('part-element').value;
    const ids=selection==='preview'?current.previewIds:selection==='all'?current.meshIds:[Number(selection)];
    const bounds=renderer.setParts(ids);
    const dd=$('part-facts').querySelector('[data-bounds]');
    if(dd)dd.textContent=bounds.map(v=>v.toLocaleString(window.PiCodeI18n?.locale,{maximumFractionDigits:2})).join(' × ')+' mm';
    renderer.reset(current);$('part-view').value='iso';schedule();
  }
  async function inspect(id,trigger) {
    const request = ++requestId;
    lastTrigger=trigger;
    const card=cards.find(card=>card.dataset.part===id);
    const title=card?.querySelector('h3').textContent || id;
    $('part-title').textContent=title;$('part-id').textContent=id;$('part-spec').textContent=card?.querySelector('.part-card-copy>p').textContent || '';$('part-facts').replaceChildren();$('part-source').hidden=true;
    current={id};$('part-static').hidden=true;$('part-static').src='/assets/parts/'+id+'.svg';$('part-static').alt=title;showModelError('Loading 3D preview…');
    dialog.showModal();document.body.classList.add('part-dialog-open');$('part-close').focus();
    current={id};
    try {
      const catalog=await data();if(!dialog.open||request!==requestId)return;
      current=catalog.items.find(item=>item.id===id);if(!current)throw Error('Unknown item');
      $('part-spec').textContent=t(current.specification);
      fact('Category',t(current.category));fact('Quantity',current.quantity===null?t('To specify'):`${current.quantity} ${t(current.unit)}`);fact('Definition',t(current.status));
      if(current.source){$('part-source').href=current.source;$('part-source').hidden=false;}
      if(!current.meshIds.length){showModelError('This item has no 3D geometry in the current revision.');return;}
      fact('Geometry bounds · W × D × H',current.previewBoundsMm.map(v=>v.toLocaleString(window.PiCodeI18n?.locale,{maximumFractionDigits:2})).join(' × ')+' mm').dataset.bounds='true';
      renderer ||= new window.PiCodePartRenderer(canvas,[]);
      await model();if(!dialog.open||request!==requestId)return;
      renderer.raw=raw;
      const element=$('part-element');element.replaceChildren();
      const addOption=(value,label)=>{const option=document.createElement('option');option.value=value;option.textContent=label;element.append(option);};
      if(current.previewIds.length!==current.meshIds.length)addOption('preview',t('One representative unit'));
      addOption('all',t('Complete item'));
      if(current.meshIds.length>1)current.meshIds.forEach((meshId,index)=>addOption(String(meshId),`${String(index+1).padStart(2,'0')} · ${raw[meshId].n}`));
      element.value=current.previewIds.length!==current.meshIds.length?'preview':'all';

      $('part-static').hidden=true;canvas.hidden=false;$('part-model-status').hidden=true;$('part-view-tools').hidden=false;$('part-help').hidden=false;$('part-bounds-note').hidden=false;
      $('part-element-label').hidden=current.meshIds.length===1;
      canvas.setAttribute('aria-label',t('Individual 3D view')+' · '+t(current.name));
      selectGeometry();
    } catch {if(dialog.open&&request===requestId)showModelError('Part geometry is unavailable. Material details remain below.');}
  }
  section.addEventListener('click',event=>{const button=event.target.closest('[data-inspect]');if(button)inspect(button.dataset.inspect,button);});
  $('part-close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
  dialog.addEventListener('close',()=>{document.body.classList.remove('part-dialog-open');requestId++;current=null;drag=null;lastTrigger?.focus({preventScroll:true});});
  $('part-element').addEventListener('change',selectGeometry);
  $('part-view').addEventListener('change',()=>{if(!renderer)return;const views={front:[0,0],back:[Math.PI,0],top:[0,Math.PI/2]};if($('part-view').value==='iso')renderer.reset(current);else [renderer.yaw,renderer.pitch]=views[$('part-view').value];renderer.zoom=1;schedule();});
  function zoom(factor){if(renderer){renderer.zoom=Math.max(.35,Math.min(4,renderer.zoom*factor));schedule();}}
  $('part-zoom-in').addEventListener('click',()=>zoom(1.15));$('part-zoom-out').addEventListener('click',()=>zoom(1/1.15));
  function reset(){renderer?.reset(current);$('part-view').value='iso';schedule();}
  $('part-reset').addEventListener('click',reset);
  canvas.addEventListener('pointerdown',event=>{if(!renderer)return;drag={x:event.clientX,y:event.clientY,yaw:renderer.yaw,pitch:renderer.pitch};canvas.setPointerCapture(event.pointerId);});
  canvas.addEventListener('pointermove',event=>{if(!drag)return;renderer.yaw=drag.yaw+(event.clientX-drag.x)*.009;renderer.pitch=Math.max(-Math.PI/2,Math.min(Math.PI/2,drag.pitch-(event.clientY-drag.y)*.009));schedule();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>drag=null);
  canvas.addEventListener('wheel',event=>{event.preventDefault();zoom(Math.exp(-event.deltaY*.001));},{passive:false});
  canvas.addEventListener('keydown',event=>{
    if(!renderer)return;
    if(event.key==='ArrowLeft')renderer.yaw-=.15;
    else if(event.key==='ArrowRight')renderer.yaw+=.15;
    else if(event.key==='ArrowUp')renderer.pitch=Math.min(Math.PI/2,renderer.pitch+.15);
    else if(event.key==='ArrowDown')renderer.pitch=Math.max(-Math.PI/2,renderer.pitch-.15);
    else if(event.key==='+'||event.key==='=')zoom(1.15);
    else if(event.key==='-')zoom(1/1.15);
    else if(event.key==='Home')reset();else return;
    event.preventDefault();schedule();
  });
  canvas.addEventListener('part-context-lost',()=>showModelError('Part geometry is unavailable. Material details remain below.'));
  new ResizeObserver(schedule).observe($('part-stage'));
})();
