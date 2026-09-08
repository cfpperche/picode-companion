(() => {
  'use strict';
  const t = message => window.PiCodeI18n?.t(message) ?? message;
  document.documentElement.classList.remove('no-js');
  const $ = id => document.getElementById(id);
  const root = $('picode-cyber-c');
  let activeMode = 'exterior';
  let activeFinish = 'graphite';
  let activeComponent = 'all';
  const finishes = {
    graphite: ["Cyberpunk graphite", "Satin body · cyan and magenta accents", "CYBERPUNK · GRAPHITE + CYAN"],
    pearl: ["Cyberpunk pearl", "Light body · cyan and magenta accents", "STUDY · PEARL + CYAN"],
    pink: ["Retro pink", "Pink body · black bezel and neon accents", "STUDY · PINK + NEON"]
  };
  const dispatch = (id, value) => { const element = $(id); element.value = value; element.dispatchEvent(new Event('change')); };
  function switchMode(value) {
    activeMode = value;
    document.querySelectorAll('[data-mode]').forEach(button => {
      const selected = button.dataset.mode === value;
      button.classList.toggle('active', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    document.querySelectorAll('[data-panel]').forEach(panel => { panel.hidden = panel.dataset.panel !== value; });
    $('explode-control').hidden = value !== 'explode';
    $('pcc-explode').value = '100';
    $('explode-value').value = '100%';
    dispatch('pcc-mode', value === 'specs' ? 'exterior' : value);
    $('pcc-dims').checked = value === 'specs';
    $('pcc-dims').dispatchEvent(new Event('change'));
    activeComponent = 'all';
    $('pcc-isolate').checked = false;
    $('selection-note').hidden = true;
    dispatch('pcc-component', 'all');
    updateSelection();
    if (window.PiCodeViewer) window.PiCodeViewer.reset();
  }
  function updateSelection() {
    document.querySelectorAll('[data-component]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.component === activeComponent));
    });
  }
  function selectComponent(key) {
    const isolate = $('pcc-isolate').checked;
    if (key === 'compute' && activeMode === 'exterior') { switchMode('inside'); $('pcc-isolate').checked = isolate; }
    if (key === 'all') $('pcc-isolate').checked = false;
    activeComponent = key;
    $('selection-note').hidden = key === 'all';
    $('pcc-shutter').hidden = key !== 'camera';
    dispatch('pcc-component', key);
    updateSelection();
    if (key !== 'all') {
      const mobile = matchMedia('(max-width: 860px)').matches;
      (mobile ? $('explorar') : $('selection-note')).scrollIntoView({ block: mobile ? 'start' : 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
    }
  }
  document.querySelectorAll('[data-mode]').forEach(button => button.addEventListener('click', () => switchMode(button.dataset.mode)));
  document.querySelectorAll('[data-component]').forEach(button => button.addEventListener('click', () => selectComponent(button.dataset.component)));
  document.querySelectorAll('[data-finish]').forEach(button => button.addEventListener('click', () => {
    activeFinish = button.dataset.finish;
    const [name, description, caption] = finishes[activeFinish];
    $('finish-name').textContent = t(name);
    $('finish-description').textContent = t(description);
    $('scene-caption').textContent = t(caption);
    document.querySelectorAll('[data-finish]').forEach(item => {
      const selected = item === button;
      item.classList.toggle('active', selected);
      item.setAttribute('aria-pressed', String(selected));
    });
    window.PiCodeViewer?.setFinish(activeFinish);
  }));
  $('pcc-isolate').addEventListener('change', () => { if ($('pcc-isolate').checked && activeComponent === 'all') selectComponent('compute'); });
  $('pcc-explode').addEventListener('input', event => {
    const value = Number(event.target.value);
    $('explode-value').value = value + '%';
    window.PiCodeViewer?.setExplosion(value / 100);
  });
  $('zoom-in').addEventListener('click', () => window.PiCodeViewer?.zoomBy(1.13));
  $('zoom-out').addEventListener('click', () => window.PiCodeViewer?.zoomBy(1 / 1.13));
  $('reset-view').addEventListener('click', () => { window.PiCodeViewer?.reset(); selectComponent('all'); });
  $('clear-selection').addEventListener('click', () => selectComponent('all'));
  document.querySelectorAll('[data-explore]').forEach(button => button.addEventListener('click', () => {
    switchMode('exterior');
    selectComponent(button.dataset.explore);
    $('explorar').scrollIntoView({ behavior: 'smooth', block: 'start' });
    $('pcc-canvas').focus({ preventScroll: true });
  }));
  window.addEventListener('picode-ready', () => {
    const component = activeComponent;
    switchMode(activeMode);
    window.PiCodeViewer.setFinish(activeFinish);
    if (component !== 'all') selectComponent(component);
    root.dataset.uiReady = 'true';
  }, { once: true });
})();
