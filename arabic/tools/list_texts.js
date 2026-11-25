// Lists every Arabic text the app can speak -> texts.json (input for make_audio.py).
// Run from the repo root: node arabic/tools/list_texts.js
const {chromium} = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + path.resolve(__dirname, '..', 'index.html'));
  const t = await p.evaluate(() => { const s = new Set(); ALL_ITEMS.forEach(i => s.add(i.say)); Object.values(LETTERS).forEach(l => s.add(l.word.ar)); return [...s].sort(); });
  require('fs').writeFileSync('texts.json', JSON.stringify(t)); console.log(t.length, 'texts -> texts.json'); await b.close();
})();
