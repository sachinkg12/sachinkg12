# Profile typography

The current visual assets follow [Sachin’s portfolio website](https://sachinkg12.github.io/): IBM Plex Sans for body text, Arial for display headings, Lora for italic serif accents, and IBM Plex Mono for small labels.

Bundled, unmodified font files from the official Google Fonts repository:

| Font | Source | Use |
| --- | --- | --- |
| Arimo | https://github.com/googlefonts/Arimo | Open-source, Arial-compatible fallback for asset generation on systems without Arial |
| IBM Plex Sans | https://github.com/google/fonts/tree/main/ofl/ibmplexsans | Current banner and supporting text |
| Lora | https://github.com/google/fonts/tree/main/ofl/lora | Current serif accents, including italic text |
| IBM Plex Mono | https://github.com/google/fonts/tree/main/ofl/ibmplexmono | Small labels |
| Space Grotesk | https://github.com/google/fonts/tree/main/ofl/spacegrotesk | Earlier typography study |
| Manrope | https://github.com/google/fonts/tree/main/ofl/manrope | Earlier typography study |
| Sora | https://github.com/google/fonts/tree/main/ofl/sora | Earlier typography study |

Each font’s SIL Open Font License is included beside its source file.
The visual-asset builder converts glyphs to SVG paths, retaining accessible labels.
Visitors do not need to install fonts or fetch a third-party font service.
The web preview loads IBM Plex Sans from the bundled file. Its font toggle can
show GitHub’s paragraph font. GitHub controls native README paragraph typography.
The section headings use outlined lettering in border-free h3 elements, so their
font pairing also appears on GitHub. Arial is read from the local operating system
when available; its font files are not copied or redistributed. Arimo provides the
portable fallback when Arial is unavailable.

Install `scripts/design-requirements.txt` in a Python environment, then run
`python3 scripts/build_profile_design.py` from the repository to regenerate assets.
The selected colors are defined in `../theme.json`.
