"""Regenerate every SVG in assets/. `python scripts/build.py [hero|cards|activity ...]`"""
import sys

import activity
import cards
import hero

STEPS = {"hero": hero.main, "cards": cards.main, "activity": activity.main}

if __name__ == "__main__":
    for name in sys.argv[1:] or STEPS:
        print(f"building {name}")
        STEPS[name]()
