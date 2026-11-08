# Profile typography

Bundled, unmodified font files from the official Google Fonts repository:

| Font | Source | Use |
| --- | --- | --- |
| Space Grotesk | https://github.com/google/fonts/tree/main/ofl/spacegrotesk | Banner and feature-card display type |
| Manrope | https://github.com/google/fonts/tree/main/ofl/manrope | Supporting text in visual assets |
| IBM Plex Mono | https://github.com/google/fonts/tree/main/ofl/ibmplexmono | Small technical labels |
| Sora | https://github.com/google/fonts/tree/main/ofl/sora | Alternative shown in the local comparison |

Each font's SIL Open Font License is included beside its source file.
The visual-asset builder converts glyphs to SVG paths, retaining accessible labels.
Visitors do not need to install fonts or fetch a third-party font service.
GitHub's normal README paragraphs, headings and tables retain GitHub typography.

To regenerate visual assets, install `scripts/design-requirements.txt` in a Python
environment and run `python3 scripts/build_profile_design.py` from the repository.

The selected palette is **Forest & Slate**, defined in `../theme.json`: deep forest
backgrounds, slate text, neutral surfaces, mint/sage highlights, and a small yellow
accent. The hand stays yellow; secondary links retain small destination markers.
