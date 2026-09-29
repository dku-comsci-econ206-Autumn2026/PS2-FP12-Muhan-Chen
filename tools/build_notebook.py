"""Rebuild PS2_trust_forfeit.ipynb so Colab can run from the notebook alone.

From the repository root:
    python tools/build_notebook.py
    jupyter nbconvert --to notebook --execute --inplace PS2_trust_forfeit.ipynb
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = (ROOT / "trust_forfeit.py").read_text(encoding="utf-8").rstrip("\n")
NB = ROOT / "PS2_trust_forfeit.ipynb"


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": _lines(text)}


def code(text):
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": _lines(text),
    }


def _lines(text):
    body = text.strip("\n") + "\n"
    return body.splitlines(keepends=True)


cells = [
    md("""
# Trust the table, not the resemblance

COMSCI/ECON 206 · Autumn 2026 Session 1 · Team FP12 · Muhan Chen

**Question.** A Promiser chooses Keep or Break. A Decider chooses Trust or Verify without seeing that choice. When does Trust become the equilibrium, and can a SAME/DIFFERENT label replace the rule that gets you there?

**Run.** Runtime → Run all. The install cell loads Nashpy. The next cell writes `trust_forfeit.py`. Inputs are synthetic. Human play is not in this notebook (`n = 0`).

| Object | Value |
|---|---|
| Decider | Trust+Keep 6, Trust+Break −4, Verify 2 |
| Aligned Promiser | Keep 6, Break 3 |
| Misaligned Promiser | Keep 6, Break 10 |
| Forfeit | 5, subtracted from a misaligned Break only; not paid to the Decider |
| `p*` | 0.6, from `10p − 4 = 2` |
| PS1 seed 206 | benchmark +48, always-Verify +24, always-Trust +22, similarity +18 |
"""),
    code("""
%pip install -q nashpy
"""),
    code("MODULE = r'''" + MODULE.replace("'''", "''' + \"'''\" + r'''") + "'''\n"
         "open('trust_forfeit.py','w',encoding='utf-8').write(MODULE)\n"
         "print('wrote', len(MODULE.splitlines()), 'lines')\n"),
    code("""
import trust_forfeit as tf

print("p* =", tf.p_star())
for row in tf.treatments():
    eq = row["equilibrium"]
    pay = row["equilibrium_payoffs"]
    label = "forfeit 5" if row["forfeit"] else "no forfeit"
    print(f"{row['alignment']:11} {label:10} {eq['decider']:6} {eq['promiser']:5} payoffs {pay['decider']}, {pay['promiser']}")
    print("  decider matrix ", row["decider_matrix"])
    print("  promiser matrix", row["promiser_matrix"])
"""),
    md("""
## What the printout is saying

Nashpy and the one-deviation scan agree. Aligned: Trust, Keep. Misaligned without a forfeit: Verify, Break, and the payoffs are 2 and 10. Misaligned with a forfeit of 5: Trust, Keep, and the payoffs are 6 and 6. The Decider's payoff when the Promiser breaks stays −4.
"""),
    code("""
print("PS1 seed 206", tf.ps1_replay(206))
print("new schedule counts", tf._count_schedule(tf.build_rounds(206)))
auction = tf.forfeit_auction((9, 6), (True, False), 206)
print("second bid 6", auction["equilibrium"], "unique", auction["unique"])
indifferent = tf.forfeit_auction((4, 4), (False, True), 206)
print("second bid 4, unique", indifferent["unique"])
assert tf.ps1_replay(206) == {"benchmark": 48, "always_verify": 24, "always_trust": 22, "similarity": 18}
assert abs(tf.p_star() - 0.6) < 1e-12
print("All checks passed.")
"""),
    md("""
## Limits

Points are illustrative. Promiser payoffs do not depend on Trust versus Verify. The twelve rounds do not carry points forward. The PS1 line replays an exogenous keep/break draw; it is not an AI playing this game. The two-bid forfeit contest is an appendix record, not the result of the paper. No human CSV is summarized here.
"""),
]

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    },
    "cells": cells,
}
NB.write_text(json.dumps(nb, indent=1) + "\n", encoding="utf-8")
print("wrote", NB)
