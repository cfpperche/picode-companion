/* One network/decompression operation shared by assembly and individual views. */
(() => {
  'use strict';
  let pending;
  window.PiCodeModel = Object.freeze({
    load() {
      if (!pending) pending = (async () => {
        const response = await fetch('/assets/companion-c04.b64?v=centered-display-1');
        if (!response.ok) throw Error('The model file could not be loaded.');
        const bytes = Uint8Array.from(atob((await response.text()).trim()), c => c.charCodeAt(0));
        const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
        return JSON.parse(await new Response(stream).text());
      })();
      return pending;
    }
  });
})();
