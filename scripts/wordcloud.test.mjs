import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {normalizeWord, submissionsFromIssues, cloudWords, layoutWords, intersects, renderSvg} from '../assets/profile/wordcloud.mjs';

const data = JSON.parse(await readFile(new URL('../assets/profile/wordcloud.json', import.meta.url), 'utf8'));
const issue = (number, author, word, extra = {}) => ({number, title: '[wordcloud] My word', body: `### Your word\n\n${word}\n`, user: {login: author, type: 'User'}, labels: [], ...extra});

test('normalizes short topics while rejecting markup, URLs and excessive input', () => {
  assert.equal(normalizeWord('  AI   Agents '), 'AI Agents');
  assert.equal(normalizeWord('Research & Tools'), 'Research & Tools');
  assert.equal(normalizeWord('日本'), '日本');
  for (const word of ['<script>alert(1)</script>', 'https://example.com', 'a', 'a'.repeat(25), 'one two three four']) assert.equal(normalizeWord(word), null);
});

test('accepts issue-form input, deduplicates people, and excludes PRs and bots', () => {
  const result = submissionsFromIssues([
    issue(1, 'alice', 'Java'), issue(4, 'alice', 'RAG'), issue(2, 'bob', 'RAG'),
    issue(5, 'bot', 'Spam', {user: {login: 'bot', type: 'Bot'}}),
    issue(6, 'carol', 'HTML', {pull_request: {}}),
    issue(7, 'dave', 'Other', {title: 'Ordinary issue'}),
    issue(8, 'eve', '<img src=x onerror=alert(1)>')
  ]);
  assert.deepEqual(result.map(s => [s.author, s.word]), [['alice', 'RAG'], ['bob', 'RAG']]);
});

test('hiding a current contribution does not reinstate an older word', () => {
  assert.deepEqual(submissionsFromIssues([issue(1, 'alice', 'Java'), issue(2, 'alice', 'RAG', {labels: [{name: 'wordcloud-hidden'}]})]), []);
});

test('matching words grow, without counting the same person twice', () => {
  const words = cloudWords({starters: [], submissions: [{word: 'Java', author: 'a'}, {word: 'JAVA', author: 'b'}, {word: 'Java', author: 'a'}]});
  assert.equal(words.length, 1);
  assert.equal(words[0].votes, 2);
});

test('starter cloud and added words fit without collisions on desktop and mobile', () => {
  const examples = [data, {...data, submissions: [{word: 'Testing', author: 'a'}, {word: '日本', author: 'b'}]}];
  for (const example of examples) for (const mobile of [false, true]) for (const seed of [0, 1, 3]) {
    const words = cloudWords(example);
    const {placed, area} = layoutWords(words, {width: mobile ? 600 : 1200, mobile, seed});
    assert.equal(placed.length, words.length, `Missing word, mobile=${mobile}, seed=${seed}`);
    for (const [i, box] of placed.entries()) {
      assert.ok(box.x >= area.x && box.y >= area.y);
      assert.ok(box.x + box.width <= area.x + area.width + 1 && box.y + box.height <= area.y + area.height + 1);
      for (const other of placed.slice(i + 1)) assert.equal(intersects(box, other), false);
    }
  }
});

test('SVG escapes text and distinguishes starter topics from real contributions', () => {
  const svg = renderSvg({...data, prompt: 'Research & Tools'});
  assert.ok(svg.includes('Research &amp; Tools'));
  assert.ok(svg.includes('STARTER TOPICS · ADD THE FIRST COMMUNITY WORD'));
  assert.ok(!svg.includes('<script'));
  assert.ok(renderSvg({...data, submissions: [{word: 'Testing', author: 'a'}]}, {preview: true}).includes('1 LOCAL PREVIEW WORD'));
});

test('a busy cloud keeps every displayed topic and all 20 new preview words', () => {
  const example = {...data, submissions: Array.from({length: 20}, (_, i) => ({word: `Community topic ${i+1}`, author: `person${i}`}))};
  const words = cloudWords(example);
  assert.equal(words.length, 30);
  for (const item of example.submissions) assert.ok(words.some(w => w.word === item.word));
  for (const mobile of [false, true]) {
    const {placed} = layoutWords(words, {width: mobile ? 600 : 1200, mobile, seed: 3});
    assert.equal(placed.length, words.length);
  }
});
