"""Shared color tokens for the GitHub profile's generated visual assets."""
from pathlib import Path
import json

THEME = json.loads((Path(__file__).resolve().parent.parent / 'assets/profile/theme.json').read_text())
