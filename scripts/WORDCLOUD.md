# Community word cloud

The GitHub README uses self-contained desktop and mobile SVGs. The local HTML
preview adds a browser-only form with add, shuffle, and reset controls. GitHub
READMEs do not run that JavaScript; their **Add your word** link opens an issue
form instead.

## Build and check locally

```sh
node scripts/build_wordcloud.mjs
node --test scripts/wordcloud.test.mjs
python3 scripts/render_profile_preview.py --output-dir /tmp/sachin-github-redesign
```

`assets/profile/wordcloud.json` holds explicitly identified starter topics and
public GitHub contributions. Starter weights set the initial visual composition;
they are not visitor votes. New contributions increase the size of matching words.
The cloud displays up to 30 of the most prominent topics to preserve readability.
The selected Forest & Slate colors come from `assets/profile/theme.json`, shared
by the static asset builder and the browser preview, including shuffled clouds.
Each GitHub account contributes one current word, taken from its latest eligible
issue. The preview keeps trial words in the current browser's local storage.

## Hosted refresh

The issue template, workflow, builder, shared module, JSON and SVG assets are
published with the README. Repository Issues and Actions must be enabled.
The `Refresh community word cloud` workflow reads issue-form submissions and
commits only the three cloud data/image files. It needs contents write and issues
read permissions, using the built-in GitHub token. It does not execute issue text
as commands, post comments, or close issues.

Use the workflow's manual **Run workflow** control to rebuild from all existing
submissions. Editing a submission replaces its word; closing an issue preserves
its contribution. Deleting an issue or applying a `wordcloud-hidden` label removes
it. Invalid input, bot accounts, pull requests and unrelated issues are excluded.
The public data retains only the word, public GitHub login and issue number.
