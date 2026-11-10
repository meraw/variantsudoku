# Setter's note — Zip It

Two line types new to this gallery, zipper lines and Dutch whispers, drawn as a zip fastener. The orange chain down column 5 is
a single Dutch whisper. Purple teeth cross it on the even rows, and longer purple teeth grow out of it on the odd rows, alternating
left and right like interlocking teeth. Short orange stitches sit in the fabric on either side.

**Facts worth finding:**
- A short tooth's centre is the sum of two different digits, so it is at least 3. That leaves very few ways to fill the chain.
  I counted 72 orders for a whole-house Dutch whisper, and only 24 of them put 3 or more on all four tooth centres.
- On a Dutch whisper, 5 can only sit next to 1 or 9, 4 next to 8 or 9, and 6 next to 1 or 2.
- The one given is not there to make the solution unique (the lines alone already do that). It is the way in.

**How it was set.** I drew the fastener myself: the chain, the teeth, and their alternation. I proved some alternatives impossible along
the way (teeth on the odd rows, a second full-column whisper). The rest came from solver-guided growth with a fallback given. I then
curated it by hand: I replaced two bent diagonal lines with straight or L-shaped ones, and made sure no purple line touches another
purple line, so you can always see where a zipper ends. One prettier draft, with orange half-rows facing every long tooth, was unique but couldn't
be solved without heavy guessing. It is in the setter's log. The short tooth on row 2 is the one redundant line: it completes the
picture but adds no information.

**Hints (light spoilers):**
- Start at the given 4 and read along row 5.
- Once the middle of the chain is known, the teeth on rows 4 and 6 have very few totals left.

Logical solvability: verified with my candidate-elimination solver (35 rounds of tier-2 logic, no guessing, no contradiction tests)
and independently with Rangsk's SudokuSolver, which knows both line types natively. It solves the puzzle with 2 contradiction tests and
one forcing chain, about the level of Pinwheel Whispers. It has **not** been test-solved by a human.
