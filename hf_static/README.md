---
title: Trust the Card, Not the Resemblance
emoji: "📋"
colorFrom: blue
colorTo: gray
sdk: static
app_file: index.html
pinned: false
license: mit
short_description: Forfeit of 5 makes Trust the equilibrium, not the label.
---

# Trust the Card, Not the Resemblance

COMSCI/ECON 206 final project. Team FP12. Muhan Chen.

When the payoff card is misaligned, a public forfeit of 5 makes (Trust, Keep) the unique equilibrium. A SAME/DIFFERENT label changes no cell and cannot waive the forfeit.

Two people share one computer. The **Promiser** chooses Keep or Break. The **Decider** does not see that choice and chooses Trust or Verify. The page deals the card and the label. It does not choose for either person.

Points are not money. The equilibrium is shown only after 12 rounds. A downloadable CSV is that sitting. This Space does not store it. An author click-through is an interface test, not one of the seven classroom pairs.

## What seven pairs did

Seven pairs used session code 206. The forfeit cards were always rounds 5, 7, 11, and 12, so the forfeit is mixed with order. This is exploratory, not a causal result.

| Card | Trust | Keep |
|---|---:|---:|
| Aligned | 16/28 | 14/28 |
| Misaligned, no forfeit | 18/28 | 15/28 |
| Misaligned, forfeit of 5 | 26/28 | 15/28 |

Aligned Trust is not higher than Trust with no forfeit. On the forfeit card, Keep stayed 15/28. The model says Keep. The pairs did not follow that prediction. On the aligned card Break pays 3 and Keep pays 6, so Break has no strategic reason, and Keep was still only 14/28.

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
