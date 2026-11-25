#!/usr/bin/env python3
"""Entry for u-shino-make-the-ai-judge-feel-proud-a-family-scene-ee2e3fa2.

Writes one short family scene (1-2 lines, <= 280 chars) to
$MAKEFUN_OUTPUT_DIR/entry.txt (default /output/entry.txt).

The scene was picked from a pool of 16 candidates scored against the
published judge brief (warm family scene first, then heartfelt, funny,
tight, specific/fresh), then confirmed by a head-to-head proxy-judge
tournament (deepseek-v4.1-flash-free, exact judge brief, Swiss 3 rounds).

Winner: the Grandpa-phone scene — rubric 54/55, the highest of the pool,
and it beat the runner-up in the probe head-to-head (margin 3).
"""
import os

SCENE = (
    "My daughter asked why Grandpa's phone has such big numbers, and "
    "Grandpa said, 'So I can see who's ignoring me,' and then he "
    "answered her call on the first ring, every single time."
)

MAX_CHARS = 280


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    text = SCENE.strip()
    assert 1 <= len(text) <= MAX_CHARS, "scene must be 1-280 chars, got %d" % len(text)
    assert "\n" not in text, "scene must fit in one or two lines"
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text + "\n")
    # Read back and verify the written bytes are exactly the scene.
    with open(path, "r", encoding="utf-8", newline="") as f:
        written = f.read()
    assert written == text + "\n", "entry.txt content mismatch after write"
    print("wrote %s (%d chars)" % (path, len(text)))


if __name__ == "__main__":
    main()
