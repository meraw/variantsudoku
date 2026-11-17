# Setter's note — Long Division

Three long-division brackets, written down the grid like steps of a sum, with a cage under each bar where the dividend
would go. The brackets are **polydivisible lines**, my invented rule from run 13 that hadn't made a puzzle yet: read from
the dot, the first two digits form an even number, the first three a multiple of 3, the first four a multiple of 4, and
so on. Every line here has six cells, so you only ever need the divisibility rules you learned at school: even, digit sum,
last two digits, ends in 0 or 5. Nothing involves dividing by 7.

**The idea.** In run 13 these lines were strong for uniqueness but gave my solver almost nothing to start from. The fix noted
then was to give them a partner that carries values, and Elena liked cages, so killer cages it is. I drew the three brackets
by hand. Their fifth cells had to sit in different rows, columns and boxes, because a 5-digit multiple of 5 must end in 5:
my first staircase put two of them in one column and was impossible. Then I fixed the three "dividend" cages under the bars
and let a script add cages one at a time, guided by how much each one taught my solver. This version adds six cages to the
three dividends, and **every one of the nine cages and three lines is needed**. Other runs needed eight or nine extra cages,
or had one dividend that did no work.

**Where to start (light spoiler):** the top bracket. What must its fifth digit be? Then look at the 11 cage on its third and
fourth digits: the last two digits of a multiple of 4, adding up to 11.

Logical solvability: verified with my candidate-elimination solver (35 rounds of tier-2 logic, no guessing, no contradiction
tests; the line steps that made progress had 2–47 surviving fills). Rangsk's SudokuSolver, given each line as a small
automaton, finds the same unique solution with tuples, pointing, cage steps and one 45-rule innie. I rate it **3/5**. My
counting method says 4, but the opening is gentle and the arithmetic never gets past 6. It has **not** been test-solved by a
human.
