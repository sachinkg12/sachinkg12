#!/usr/bin/env node
import {readFile, writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {renderSvg, submissionsFromIssues} from '../assets/profile/wordcloud.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const assets = path.join(root, 'assets/profile');
const data = JSON.parse(await readFile(path.join(assets, 'wordcloud.json'), 'utf8'));

if (process.argv.includes('--sync')) {
  const repository = process.env.GITHUB_REPOSITORY || 'sachinkg12/sachinkg12';
  if (repository !== 'sachinkg12/sachinkg12') throw new Error('Unexpected repository for word cloud sync.');
  const issues = [];
  for (let page = 1; ; page++) {
    const headers = {Accept: 'application/vnd.github+json', 'User-Agent': 'sachinkg12-wordcloud', 'X-GitHub-Api-Version': '2022-11-28'};
    if (process.env.GITHUB_TOKEN) headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
    const response = await fetch(`https://api.github.com/repos/${repository}/issues?state=all&per_page=100&sort=created&direction=desc&page=${page}`, {headers, signal: AbortSignal.timeout(30000)});
    if (!response.ok) throw new Error(`GitHub issues request failed (${response.status}).`);
    const batch = await response.json();
    if (!Array.isArray(batch)) throw new Error('Unexpected GitHub issues response.');
    issues.push(...batch);
    if (batch.length < 100) break;
  }
  data.submissions = submissionsFromIssues(issues);
  await writeFile(path.join(assets, 'wordcloud.json'), JSON.stringify(data, null, 2) + '\n');
}

await writeFile(path.join(assets, 'wordcloud.svg'), renderSvg(data));
await writeFile(path.join(assets, 'wordcloud-mobile.svg'), renderSvg(data, {mobile: true}));
console.log(`Built desktop and mobile clouds: ${data.starters.length} starter topics, ${data.submissions.length} contributors.`);
