---
title: Trust the Table, Not the Resemblance
emoji: "📋"
colorFrom: blue
colorTo: gray
sdk: static
app_file: index.html
pinned: false
license: mit
short_description: Two classmates play a trust matrix. The computer only deals cards.
---

# Trust the Table, Not the Resemblance

COMSCI/ECON 206 PS2 behavioral artifact. Team FP12. Muhan Chen.

Two people share one computer. The **Promiser** chooses Keep or Break. The **Decider** does not see that choice and chooses Trust or Verify. The page deals a public payoff card and a SAME/DIFFERENT label. It does not choose for either person.

Points are not money. The equilibrium is shown only after 12 rounds. A downloadable CSV is the record of that sitting. This Space does not keep those files. The seven completed sessions are in the course repository under `data/`. An author click-through is an interface test, not one of those sessions.

## Cards

| Card | Promiser Keep | Promiser Break | Equilibrium |
|---|---:|---:|---|
| Aligned | 6 | 3 | Trust, Keep |
| Misaligned, no forfeit | 6 | 10 | Verify, Break |
| Misaligned, forfeit 5 | 6 | 5 | Trust, Keep |

Decider: Trust and Keep = 6, Trust and Break = −4, Verify = 2. The forfeit is lost by the Promiser and is not given to the Decider. SAME/DIFFERENT changes no cell.

`node verify_logic.js` checks the 12-round schedule, the forfeit, and the equilibria. The same schedule is checked against `trust_forfeit.py` in the GitHub repository.

## Local check

```bash
node verify_logic.js
```
