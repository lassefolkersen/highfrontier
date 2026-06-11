"""Shared pytest configuration for High Frontier.

The game uses pygame at import time in a few modules.  These defaults let the
existing test suite and future GUI smoke tests run on headless CI runners.
"""

import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
