// Propagate the preview's content version to the renderer and its theme import.
const cloudVersion = new URL(import.meta.url).search;
const {normalizeWord, renderSvg} = await import(`./wordcloud.mjs${cloudVersion}`);

const demo = document.querySelector('[data-cloud-demo]');
const picture = document.querySelector('[data-cloud-picture]');
if (demo && picture) {
  const data = await fetch('./assets/profile/wordcloud.json', {cache: 'no-store'}).then(r => {if (!r.ok) throw new Error('Cloud data could not load.'); return r.json();});
  const initial = structuredClone(data);
  const form = demo.querySelector('form');
  const input = demo.querySelector('input');
  const status = demo.querySelector('[role="status"]');
  const baseCount = initial.submissions.length;
  let seed = 0;
  let localWords = [];
  try { localWords = JSON.parse(localStorage.getItem('sachin-wordcloud-preview-v1') || '[]').filter(normalizeWord).slice(0, 20); } catch { /* An unavailable browser store should not disable the demo. */ }
  function paint() {
    data.submissions = [...initial.submissions, ...localWords.map((word, i) => ({word, author: `local-preview-${i}`}))];
    const svgUrl = mobile => 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(renderSvg(data, {mobile, seed, preview: localWords.length > 0, previewCount: localWords.length}));
    picture.querySelector('source').srcset = svgUrl(true);
    picture.querySelector('img').src = svgUrl(false);
    picture.querySelector('img').alt = `${data.prompt} ${localWords.length} ${localWords.length === 1 ? 'word' : 'words'} added in this local preview; ${baseCount} community contributors.`;
    try { localStorage.setItem('sachin-wordcloud-preview-v1', JSON.stringify(localWords)); } catch { /* The in-memory preview remains usable. */ }
  }
  form.addEventListener('submit', event => {
    event.preventDefault();
    const word = normalizeWord(input.value);
    if (!word) { status.textContent = 'Use 2–24 characters and up to three words. Letters, numbers, spaces and simple punctuation are welcome.'; input.focus(); return; }
    if (localWords.some(w => w.toLocaleLowerCase('en') === word.toLocaleLowerCase('en'))) { status.textContent = 'That word is already in your preview. Try another.'; return; }
    if (localWords.length >= 20) { status.textContent = 'This demo holds 20 local words. Reset to try a fresh cloud.'; return; }
    localWords.push(word);
    paint();
    input.value = '';
    status.textContent = `“${word}” added to your local preview. Nothing was sent to GitHub.`;
    input.focus();
  });
  demo.querySelector('[data-shuffle-cloud]').addEventListener('click', () => {seed++; paint(); status.textContent = 'A fresh arrangement of the same words.';});
  demo.querySelector('[data-reset-cloud]').addEventListener('click', () => {localWords = []; seed = 0; paint(); status.textContent = 'Reset to the original starter topics.';});
  paint();
}
