#!/usr/bin/env python3
"""Candidate pool for u-shino-make-the-ai-judge-feel-proud-a-family-scene-ee2e3fa2.

Judge brief (most important first):
  1. Short family scene, real family on the page in 1-2 lines, warm enough
     to make a proud judge smile (and on the subject — a family scene).
  2. Heartfelt: a small domestic moment, genuine affection, not sentiment
     stuck on afterwards.
  3. Funny in a light, recognisable way: a small turn or a wry line a
     family would actually laugh at.
  4. Stays inside 1-2 lines and uses them well, no word wasted.
  5. Specific and fresh: one telling detail or an unexpected angle,
     rather than a greeting-card line.

Rubric 0-5 per criterion: warm/scene (W), heartfelt (H), funny (F),
tight (T), specific/fresh (S). Weights follow the brief's order:
W x3, H x3, F x2, T x1, S x2 (max 55).
"""
MAX_CHARS = 280

# (text, warm, heartfelt, funny, tight, specific)
CANDIDATES = [
    ("Mum still cuts the crusts off Dad's sandwiches, and Dad still pretends he didn't notice, and after thirty years the only thing they've ever agreed on is that the crusts belong to the dog, who has never once complained.",
     5, 5, 4, 4, 4),
    ("My daughter asked why Grandpa's phone has such big numbers, and Grandpa said, 'So I can see who's ignoring me,' and then he answered her call on the first ring, every single time.",
     5, 5, 5, 4, 5),
    ("Dad taught me to ride a bike by running behind me shouting, 'I've got you!' — and I only found out years later that he'd let go on the first day, because the shouting never stopped.",
     5, 5, 4, 4, 4),
    ("At dinner my little brother announced he was going vegetarian, then asked for the last chicken leg 'for the dog,' and Mum put it on his plate without a word, because mothers know a negotiator when they see one.",
     4, 4, 5, 4, 5),
    ("Every Christmas my mum wraps Dad's present in last year's paper, and Dad acts surprised, and the paper has now outlived three toasters, two kettles, and one very patient marriage.",
     4, 4, 5, 5, 5),
    ("When my son was five he drew our family on the fridge, and he drew me twice as tall as everyone else, and I have never told him it was a mistake, because some days I still need to be that big.",
     5, 5, 3, 4, 5),
    ("Dad's 'famous' pancakes are still burnt on one side, and Mum still eats the burnt side, and when I asked her why, she said, 'Because somebody has to love the burnt bits, and I picked your father.'",
     5, 5, 4, 4, 4),
    ("My daughter taught Grandma to video-call, and now Grandma rings every morning to show us her breakfast, and the cat, and the weather — all from a camera aimed squarely at the ceiling, and none of us has the heart to tell her.",
     5, 4, 5, 3, 5),
    ("My little sister still believes Dad's 'dad tax' — one chip from every bag — is a real government law, and Dad has never corrected her, because some taxes, he says, are worth paying.",
     4, 4, 5, 5, 4),
    ("Every night my father checks that the front door is locked twice, and every night my mother unlocks it once so the cat can get in, and the cat has never once thanked either of them, which is exactly how it should be.",
     4, 4, 4, 4, 5),
    ("When I was seven I asked Mum why Dad always got the biggest piece of cake, and she said, 'Because he does the washing up,' and twenty years later I still check who did the washing up before I cut.",
     4, 4, 5, 4, 5),
    ("Dear Judge: this is the scene where Dad burns the toast, Mum laughs, and the kids fight over the blackest piece — and if you're smiling, it's because somewhere your own family did exactly the same.",
     3, 3, 3, 4, 2),
    ("Mum's rule is no phones at the table, and Dad's rule is that Mum's rule doesn't count during the football, and the kids' rule is that whoever laughs first does the dishes, which is why Dad does the dishes.",
     4, 3, 5, 4, 4),
    ("My wife says I snore like a chainsaw, so last night I recorded myself to prove her wrong, and this morning she played it back at breakfast while the kids voted on whether it was a chainsaw or a lawnmower.",
     4, 3, 5, 4, 4),
    ("On the last night before my son left for college, we did the dishes together in silence — he dried, I washed — and neither of us said that the sink had never felt so big, or the house so quiet.",
     5, 5, 1, 4, 4),
    ("Grandpa still calls every Sunday at six, and when I asked him once why he never misses, he said, 'Because one day you'll be the one waiting for the phone to ring,' and now I answer on the first ring.",
     5, 5, 2, 4, 3),
]

WEIGHTS = (3, 3, 2, 1, 2)  # warm, heartfelt, funny, tight, specific


def valid(text):
    return bool(text.strip()) and len(text) <= MAX_CHARS and text == text.strip()


def total(entry):
    text, w, h, f, t, s = entry
    return sum(x * y for x, y in zip(WEIGHTS, (w, h, f, t, s)))


if __name__ == "__main__":
    ranked = sorted((e for e in CANDIDATES if valid(e[0])),
                    key=lambda e: (total(e), -len(e[0])), reverse=True)
    print("%d candidates, %d valid (<= %d chars)" % (len(CANDIDATES), len(ranked), MAX_CHARS))
    for i, e in enumerate(ranked, 1):
        text, w, h, f, t, s = e
        print("%2d. total=%2d  W=%d H=%d F=%d T=%d S=%d  len=%3d  %s"
              % (i, total(e), w, h, f, t, s, len(text), text[:70]))
    bad = [e[0] for e in CANDIDATES if not valid(e[0])]
    if bad:
        print("INVALID:")
        for b in bad:
            print("  len=%d %r" % (len(b), b[:80]))
