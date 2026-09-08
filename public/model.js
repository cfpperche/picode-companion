/* One network/decompression operation shared by assembly and individual views. */
(() => {
  'use strict';
  let pending;
  window.PiCodeModel = Object.freeze({
    load() {
      if (!pending) pending = (async () => {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 20000);
        let response;
        try { response = await fetch('/assets/companion-c04.b64?v=centered-display-1', { signal: controller.signal });
          if (!response.ok) throw Error('The model file could not be loaded.');
          const text = await response.text();
          return await decode(text);
        } finally { clearTimeout(timeout); }
      })().catch(error => { pending = undefined; throw error; });
      return pending;
    }
  });
  async function decode(text) {
        const bytes = Uint8Array.from(atob(text.trim()), c => c.charCodeAt(0));
        const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
        return JSON.parse(await new Response(stream).text());
  }
})();
