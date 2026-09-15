#!/usr/bin/env python3
"""
Transcript Corpus Setup Script for Lenny Growth Assistant.

Clones the Lenny Podcast transcripts repository into data/transcripts/source.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/ChatPRD/lennys-podcast-transcripts.git"
TARGET_DIR = Path(__file__).parent.parent / "data" / "transcripts" / "source"


def setup_transcripts():
    print(f"Checking transcript directory: {TARGET_DIR}")

    if TARGET_DIR.exists() and any(TARGET_DIR.iterdir()):
        print("Transcript corpus already exists in data/transcripts/source. Skipping clone.")
        return

    TARGET_DIR.parent.mkdir(parents=True, exist_ok=True)
    print(f"Cloning raw transcripts from {REPO_URL} into {TARGET_DIR}...")

    try:
        subprocess.run(
            ["git", "clone", REPO_URL, str(TARGET_DIR)],
            check=True,
        )
        print("Transcript corpus cloned successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning transcript repository: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Git executable not found in PATH. Please install git and retry.")
        sys.exit(1)


if __name__ == "__main__":
    setup_transcripts()
