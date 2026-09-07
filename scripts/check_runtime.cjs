const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '..');
const cases = {
  en: ['en', 'Open shutter', '4 microphones', 'Cyberpunk pearl'],
  pt: ['pt-BR', 'Abrir obturador', '4 microfones', 'Pérola cyberpunk'],
  es: ['es', 'Abrir obturador', '4 micrófonos', 'Perla cyberpunk']
};
for (const [locale, expected] of Object.entries(cases)) {
  const context = { window: {} };
  vm.runInNewContext(fs.readFileSync(path.join(root, `public/locales/${locale}.js`), 'utf8'), context);
  const i18n = context.window.PiCodeI18n;
  assert.equal(i18n.locale, expected[0]);
  assert.equal(i18n.t('Open shutter'), expected[1]);
  assert.equal(i18n.t('4 microphones'), expected[2]);
  assert.equal(i18n.t('Cyberpunk pearl'), expected[3]);
  assert.equal(i18n.t('Unknown diagnostic'), 'Unknown diagnostic');
  const catalog = JSON.parse(fs.readFileSync(path.join(root, `locales/${locale}.json`), 'utf8'));
  assert.equal(JSON.stringify(i18n.messages), JSON.stringify(catalog));
  console.log(`${locale}: runtime messages and fallback verified`);
}
