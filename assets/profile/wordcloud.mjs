// Shared by the static GitHub asset builder and the local interactive preview.
// No dependencies, network calls, or executable content in generated SVGs.
// Keep all shuffle variants within the approved palette: no purple, violet or magenta.
const themeUrl = new URL('./theme.json', import.meta.url);
themeUrl.search = new URL(import.meta.url).search;
const {default: THEME} = await import(themeUrl.href, {with: {type: 'json'}});
export const PALETTE = THEME.cloud;

export function normalizeWord(value) {
  if (typeof value !== 'string') return null;
  const word = value.normalize('NFKC').trim().replace(/\s+/gu, ' ');
  if (word.length < 2 || [...word].length > 24 || word.split(' ').length > 3) return null;
  // Accept names and topics, but never markup, links, control characters or code.
  return /^[\p{L}\p{N}][\p{L}\p{M}\p{N} &+#'.-]*$/u.test(word) ? word : null;
}

const xml = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&apos;'}[c]));
const key = word => word.toLocaleLowerCase('en-US');

export function submissionsFromIssues(issues) {
  const people = new Set();
  const submissions = [];
  // One current word per person; the latest eligible issue replaces older ones.
  for (const issue of [...issues].sort((a, b) => b.number - a.number)) {
    if (issue.pull_request || !issue.title?.startsWith('[wordcloud]') || issue.user?.type !== 'User') continue;
    const author = issue.user.login;
    if (!author || people.has(author)) continue;
    const hidden = issue.labels?.some(label => (typeof label === 'string' ? label : label.name) === 'wordcloud-hidden');
    if (hidden) { people.add(author); continue; }
    const match = (issue.body || '').match(/^### Your word\s*\n+([^\n]+)(?:\n|$)/m);
    const word = normalizeWord(match?.[1]);
    if (!word) continue;
    people.add(author);
    submissions.push({word, author, issue: issue.number});
  }
  return submissions.sort((a, b) => a.author.localeCompare(b.author, 'en'));
}

export function cloudWords(data) {
  const words = new Map();
  for (const item of data.starters || []) {
    const word = normalizeWord(item.word);
    if (word) words.set(key(word), {word, weight: Math.max(1, Number(item.weight) || 1), votes: 0});
  }
  const people = new Set();
  for (const item of data.submissions || []) {
    const word = normalizeWord(item.word);
    if (!word || !item.author || people.has(item.author)) continue;
    people.add(item.author);
    const entry = words.get(key(word)) || {word, weight: 3, votes: 0};
    entry.weight += 5;
    entry.votes += 1;
    words.set(key(word), entry);
  }
  return [...words.values()].sort((a, b) => b.weight - a.weight || a.word.localeCompare(b.word, 'en')).slice(0, 30);
}

function textWidth(word, size) {
  let units = 0;
  for (const c of word) {
    if (/[\u2e80-\uffff]/u.test(c)) units += 1.08;
    else if (/[MW@&]/.test(c)) units += .92;
    else if (/[ilIjtfr .']/u.test(c)) units += .4;
    else if (/[A-Z]/.test(c)) units += .74;
    else units += .64;
  }
  return units * size + 12;
}

export function intersects(a, b) {
  return a.x < b.x + b.width && a.x + a.width > b.x && a.y < b.y + b.height && a.y + a.height > b.y;
}

export function layoutWords(words, {width = 1200, mobile = false, seed = 0, scale = 1} = {}) {
  const area = {x: mobile ? 22 : 40, y: 142, width: width - (mobile ? 44 : 80), height: mobile ? 352 : 304};
  const placed = [];
  const maxWeight = Math.max(1, ...words.map(w => w.weight));
  for (const [index, item] of words.entries()) {
    const targetSize = ((mobile ? 15 : 17) + Math.sqrt(item.weight / maxWeight) * (mobile ? 27 : 39)) * scale;
    let found = false;
    for (let shrink = 0; shrink < 12 && !found; shrink++) {
      const size = Math.max(12, Math.round(targetSize * (.86 ** shrink)));
      const boxWidth = Math.ceil(textWidth(item.word, size));
      const boxHeight = Math.ceil(size * 1.24 + 6);
      if (boxWidth > area.width || boxHeight > area.height) continue;
      for (let step = 0; step < 1900; step++) {
        const radius = Math.sqrt(step / 1899);
        const angle = step * 2.399963 + seed * .79;
        const cx = area.x + area.width / 2 + Math.cos(angle) * radius * (area.width - boxWidth) / 2;
        const cy = area.y + area.height / 2 + Math.sin(angle) * radius * (area.height - boxHeight) / 2;
        const box = {x: Math.round(cx - boxWidth / 2), y: Math.round(cy - boxHeight / 2), width: boxWidth, height: boxHeight};
        if (placed.some(other => intersects(box, other))) continue;
        placed.push({...item, ...box, size, color: PALETTE[(index + seed) % PALETTE.length]});
        found = true;
        break;
      }
      // Use the remaining edge pockets before giving up on a smaller word.
      if (!found && shrink >= 2) {
        for (let y = area.y; y + boxHeight <= area.y + area.height && !found; y += 4) {
          for (let x = area.x; x + boxWidth <= area.x + area.width; x += 4) {
            const box = {x, y, width: boxWidth, height: boxHeight};
            if (placed.some(other => intersects(box, other))) continue;
            placed.push({...item, ...box, size, color: PALETTE[(index + seed) % PALETTE.length]});
            found = true;
            break;
          }
        }
      }
    }
  }
  if (placed.length < words.length && scale > .35) return layoutWords(words, {width, mobile, seed, scale: scale * .9});
  return {placed, area};
}

export function renderSvg(data, {mobile = false, seed = 0, preview = false, previewCount = 0} = {}) {
  const width = mobile ? 600 : 1200;
  const height = mobile ? 568 : 510;
  const margin = mobile ? 26 : 40;
  const words = cloudWords(data);
  const {placed} = layoutWords(words, {width, mobile, seed});
  const contributors = new Set((data.submissions || []).filter(s => normalizeWord(s.word)).map(s => s.author)).size;
  const localCount = previewCount || contributors;
  const footer = preview && localCount ? `${localCount} LOCAL PREVIEW ${localCount === 1 ? 'WORD' : 'WORDS'} · STARTER TOPICS` : contributors ? `${contributors} ${contributors === 1 ? 'CONTRIBUTOR' : 'CONTRIBUTORS'} · ${data.starters.length} STARTER TOPICS` : 'STARTER TOPICS · ADD THE FIRST COMMUNITY WORD';
  const wordMarkup = placed.map(item => `<text x="${item.x + item.width / 2}" y="${item.y + item.height / 2}" text-anchor="middle" dominant-baseline="central" font-size="${item.size}" font-weight="${item.weight >= 7 ? 650 : 450}" fill="${item.color}">${xml(item.word)}</text>`).join('\n');
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="cloud-title cloud-desc">
<title id="cloud-title">${xml(data.prompt)}</title><desc id="cloud-desc">${xml(footer)}. Topics: ${xml(placed.map(w => w.word).join(', '))}.</desc>
<defs><linearGradient id="cloud-bg" x2="1" y2="1"><stop stop-color="${THEME.base}"/><stop offset="1" stop-color="${THEME.base2}"/></linearGradient><radialGradient id="cloud-glow"><stop stop-color="${THEME.primary}" stop-opacity=".11"/><stop offset="1" stop-color="${THEME.primary}" stop-opacity="0"/></radialGradient><pattern id="cloud-dots" width="26" height="26" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="${THEME.light}" opacity=".09"/></pattern></defs>
<rect x="1" y="1" width="${width-2}" height="${height-2}" rx="18" fill="url(#cloud-bg)" stroke="${THEME.primary}"/><rect width="${width}" height="${height}" rx="18" fill="url(#cloud-dots)"/><ellipse cx="${width/2}" cy="${height/2}" rx="${width/2}" ry="${height/2}" fill="url(#cloud-glow)"/>
<g font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif">
<text x="${margin}" y="38" fill="${THEME.light}" font-family="ui-monospace,Consolas,monospace" font-size="${mobile ? 12 : 13}" letter-spacing="1.8">COMMUNITY / WORD CLOUD</text>
<text x="${margin}" y="84" fill="#f1f5f9" font-size="${mobile ? 31 : 34}" font-weight="600" letter-spacing="-.7">${xml(data.prompt)}</text>
<text x="${margin}" y="116" fill="${THEME.light}" font-size="${mobile ? 16 : 18}">A topic, a curiosity, or a shared interest.</text>
${wordMarkup}
<path d="M${margin} ${height-54}H${width-margin}" stroke="${THEME.primary}"/>
<text x="${margin}" y="${height-24}" fill="${THEME.light}" font-family="ui-monospace,Consolas,monospace" font-size="${mobile ? 11 : 12}" letter-spacing=".6">${xml(footer)}</text>
${mobile ? '' : `<text x="${width-margin}" y="${height-24}" fill="${THEME.highlight}" font-size="13" text-anchor="end">Your word belongs here ↗</text>`}
</g></svg>\n`;
}
