# HeapLens marketplace counts

`refresh_heaplens_stats.py` reads the public APIs for Visual Studio Marketplace,
Open VSX and JetBrains Marketplace, then updates the dated JSON record, desktop
and mobile SVGs, and only the marked HeapLens block in `README.md`. The visible block contains
just the heading and the three metrics cards; it does not regenerate the removed
explanatory footnote or distribution caption. Full source counters remain in JSON.

The GitHub Actions workflow runs daily at 06:15 UTC, on manual dispatch,
and when the refresh code changes on `main`.
It uses the repository's built-in token to commit the four count files; marketplace
requests use no publisher credentials. The older live-profile workflow is unchanged.

## Measures

- VS Code `downloadCount` and `install` are displayed separately. `updateCount`
  is not added to either number.
- The owner's acquisition dashboard screenshot reports **15,832 lifetime
  acquisitions**, recorded November 21, 2026. This value and its date are preserved
  separately; the public API sum is not assumed to reproduce the dashboard.
- Open VSX `downloadCount` and JetBrains `downloads` supply their download counts.
- The page does not add acquisitions, downloads and installs into one total or
  describe any of them as unique users.

The public API responses during verification were not identical: one returned
13,477 VS Code downloads and 2,319 installs; a later response returned 13,440
and 2,317. Neither sum is assumed to equal dashboard acquisitions. The available
evidence does not establish the cause of the remaining discrepancy. The dashboard screenshot is
not copied into the public repository because it contains account information.
Exact automatic refresh of that authenticated dashboard measure would require a
verified publisher-report integration; this workflow refreshes public counters.

## Run locally

```sh
python3 -m pip install -r scripts/design-requirements.txt
python3 -m unittest discover -s scripts -p 'test_heaplens_stats.py'
python3 scripts/refresh_heaplens_stats.py
python3 scripts/render_profile_preview.py --output-dir /tmp/sachin-github-redesign
```

The updater validates extension identity and all three API responses before
rendering or writing. A failed request or invalid response leaves the previous
counts and their date intact; it never substitutes zero for an unavailable count.
The data's `as_of` date follows America/Los_Angeles. A completed request can report
zero, which is a valid count and is distinct from a missing field.

Sources: [VS Code publisher reports](https://code.visualstudio.com/api/working-with-extensions/publishing-extension#review-extension-installs-and-ratings),
[Open VSX public API](https://open-vsx.org/api/guptasachinn/heaplens),
[JetBrains public plugin information](https://plugins.jetbrains.com/api/plugins/35004).
