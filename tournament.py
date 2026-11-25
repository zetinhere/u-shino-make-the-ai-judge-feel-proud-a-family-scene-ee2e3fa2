#!/usr/bin/env python3
"""Head-to-head proxy-judge tournament for the family-scene bounty.

Proxy judge: deepseek-v4.1-flash-free via 100milionseek (hms.py), standing
in for the house judge (z-ai/glm-5.3-flash) with the EXACT published
judge brief. Swiss, 3 rounds, each game judged twice (both label orders),
house scoring: the picked entry gets 0.5 + margin/10, the other gets the
rest; a call with no verdict gives 0.5-0.5. A game is the mean of its two
calls. Failed calls (503/timeout) after 3 tries score 0.5-0.5.

Usage: python3 tournament.py [--finalists N] [--out tournament.json]
"""
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, ".")
from candidates import CANDIDATES, total, valid  # noqa: E402

HMS = "/home/hatch/workspace/custom-connectors/custom.100milionseek/bin/hms.py"

BRIEF = """You are a warm, proud judge of small family scenes, reading for the line that makes a household feel loved.

Each entry is one short family scene of one or two lines, written to be warm, funny and heartfelt. You will be shown two scenes, Entry A and Entry B. Pick the scene that would make you proudest.

Weigh them on these, most important first:
1. Is a short family scene, real family on the page in a line or two, warm enough to make a proud judge smile, and loses to any entry on the subject.
2. Feels heartfelt, a small domestic moment that lands with genuine affection rather than sentiment stuck on afterwards.
3. Is funny in a light, recognisable way, a small turn or a wry line a family would actually laugh at.
4. Stays inside one or two lines and uses them well, a whole small scene in a breath with no word wasted.
5. Feels specific and fresh, one telling detail or an unexpected angle rather than a greeting-card line.

A scene can be quiet or silly; both can win. Length for its own sake does not count.

Two scenes are rarely equally warm, funny and moving. Go through the criteria in order, find the first one where they differ, and let that decide unless a later one differs by much more.

Compare the two against those criteria, pick the one that meets them better with no tie, and answer with a short reason, a verdict naming A or B, and a margin from 1 (by a hair) to 5 (overwhelmingly better).

Entry A:
{a}

Entry B:
{b}

End your answer with exactly these two lines:
VERDICT: A
MARGIN: 3
"""


def judge_once(a, b, tries=3):
    """One call, A vs B as labelled. Returns (picked, margin) or None."""
    prompt = BRIEF.format(a=a, b=b)
    for attempt in range(tries):
        try:
            r = subprocess.run(
                ["python3", HMS, prompt, "--max-tokens", "600"],
                capture_output=True, text=True, timeout=150)
            out = r.stdout or ""
            m = re.search(r"VERDICT:\s*([AB])", out)
            mg = re.search(r"MARGIN:\s*([1-5])", out)
            if m and mg:
                return m.group(1), int(mg.group(1))
        except Exception as e:
            print("  call failed (attempt %d): %s" % (attempt + 1, e), flush=True)
        time.sleep(2)
    return None


def play_game(i, j, texts):
    """One game between finalists i and j: two calls, both label orders.
    Returns (score_i, score_j) as shares of a win."""
    res1 = judge_once(texts[i], texts[j])
    res2 = judge_once(texts[j], texts[i])
    s_i = s_j = 0.0
    for res, first_is_i in ((res1, True), (res2, False)):
        if res is None:
            s_i += 0.5
            s_j += 0.5
            continue
        picked, margin = res
        win_share = 0.5 + margin / 10.0
        if (picked == "A") == first_is_i:
            s_i += win_share
            s_j += 1.0 - win_share
        else:
            s_j += win_share
            s_i += 1.0 - win_share
    return s_i / 2.0, s_j / 2.0


def swiss_pairings(points, played):
    """Pair by points desc; avoid rematches when possible."""
    order = sorted(range(len(points)), key=lambda k: (-points[k], k))
    pairs = []
    used = set()
    for idx, a in enumerate(order):
        if a in used:
            continue
        for b in order[idx + 1:]:
            if b not in used and (a, b) not in played and (b, a) not in played:
                pairs.append((a, b))
                used.add(a)
                used.add(b)
                break
        else:
            # no fresh opponent left; take the next unused one
            for b in order[idx + 1:]:
                if b not in used:
                    pairs.append((a, b))
                    used.add(a)
                    used.add(b)
                    break
    return pairs


def main():
    n = int(sys.argv[sys.argv.index("--finalists") + 1]) if "--finalists" in sys.argv else 12
    out_path = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "tournament.json"
    ranked = sorted((e for e in CANDIDATES if valid(e[0])),
                    key=lambda e: (total(e), -len(e[0])), reverse=True)
    finalists = ranked[:n]
    texts = [e[0] for e in finalists]
    points = [0.0] * n
    played = set()
    games = []
    for rnd in range(3):
        pairs = swiss_pairings(points, played)
        print("Round %d pairings: %s" % (rnd + 1, pairs), flush=True)
        with ThreadPoolExecutor(max_workers=4) as ex:
            results = list(ex.map(lambda p: play_game(p[0], p[1], texts), pairs))
        for (a, b), (sa, sb) in zip(pairs, results):
            played.add((a, b))
            points[a] += sa
            points[b] += sb
            games.append({"round": rnd + 1, "a": a, "b": b, "sa": sa, "sb": sb})
            print("  R%d %d vs %d -> %.2f / %.2f" % (rnd + 1, a, b, sa, sb), flush=True)
        print("  standings: %s" % sorted(
            ((round(p, 2), i) for i, p in enumerate(points)), reverse=True), flush=True)
    standings = sorted(range(n), key=lambda k: (-points[k], -total(finalists[k]), -len(texts[k])))
    result = {
        "finalists": [{"text": t, "rubric": total(e), "points": points[i]}
                      for i, (e, t) in enumerate(zip(finalists, texts))],
        "standings": standings,
        "games": games,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("\nFINAL STANDINGS (points / 3.0):")
    for rank, i in enumerate(standings, 1):
        print("%2d. %.2f  rubric=%2d  len=%3d  %s"
              % (rank, points[i], total(finalists[i]), len(texts[i]), texts[i][:75]))
    print("saved to", out_path)


if __name__ == "__main__":
    main()
