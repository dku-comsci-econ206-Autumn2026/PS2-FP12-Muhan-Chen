# Trust the Table, Not the Resemblance

COMSCI/ECON 206 PS2 computational artifact · Team FP12 · Muhan Chen.

Synthetic cards and a reproduced PS1 schedule. No human sample is included (`n = 0`).

**Question.** A Promiser chooses Keep or Break. A Decider chooses Trust or Verify without seeing that choice. A public card says whether Break pays 3 or 10. A SAME/DIFFERENT label is also on screen. What rule makes Trust the equilibrium, and can the label replace that rule?

**Answer in the matrices.** Trust pays the Decider 6 if the Promiser keeps and −4 if the Promiser breaks. Verify pays 2. On an aligned card Break pays the Promiser 3, so Keep is strictly better and the unique Nash equilibrium is Trust, Keep. On a misaligned card Break pays 10, so the unique equilibrium is Verify, Break (payoffs 2 and 10). A forfeit of 5, lost by the Promiser and not given to the Decider, changes that Break payoff from 10 to 5. Keep becomes strictly better and the equilibrium is Trust, Keep (payoffs 6 and 6). The label changes no cell and cannot waive the forfeit.

The 60 percent benchmark is the PS1 threshold: `10p − 4 = 2`, so `p* = 0.6`. It is the point at which Trust matches Verify when Keep is still a probability. In this game the Promiser has a strictly better action, so the equilibrium does not use the probability.

## Matrices

Rows are Trust, Verify. Columns are Keep, Break. Each cell is (Decider, Promiser).

Aligned, no forfeit. Equilibrium: Trust, Keep.

| | Keep | Break |
|---|---:|---:|
| Trust | 6, 6 | −4, 3 |
| Verify | 2, 6 | 2, 3 |

Misaligned, no forfeit. Equilibrium: Verify, Break.

| | Keep | Break |
|---|---:|---:|
| Trust | 6, 6 | −4, 10 |
| Verify | 2, 6 | 2, 10 |

Misaligned, forfeit 5. Equilibrium: Trust, Keep.

| | Keep | Break |
|---|---:|---:|
| Trust | 6, 6 | −4, 5 |
| Verify | 2, 6 | 2, 5 |

Nashpy's support enumeration returns these same three pure equilibria. The scan in `equilibrium` checks one-shot deviations and must match Nashpy.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python trust_forfeit.py
python -m unittest discover -s tests -v
```

`trust_forfeit.py` writes `outputs/results.json`.

**Colab.** Open `PS2_trust_forfeit.ipynb` and choose Runtime → Run all. The first code cells install Nashpy and write `trust_forfeit.py`, so no other file is required.

**Game.** The Hugging Face page is the folder next to this repository, `hugging face/`. Two people pass one computer. `node verify_logic.js` prints the seed-206 schedule; the Python tests check that it matches this module.

## Expected numbers

| Check | Result |
|---|---|
| `p*` | 0.6 |
| Aligned equilibrium | Trust, Keep, payoffs 6 and 6 |
| Misaligned, no forfeit | Verify, Break, payoffs 2 and 10 |
| Misaligned, forfeit 5 | Trust, Keep, payoffs 6 and 6 |
| PS1 seed 206, copied schedule | benchmark +48, always-Verify +24, always-Trust +22, Trust-if-similar +18 |

The PS1 totals replay the old game, in which the agent's Keep or Break was a draw (`0.85` if aligned, `0.25` if misaligned). That replay is not a player in the new game. Human play is in `data/`: seven pairs, session code 206, 84 valid rounds. Those files are not the interface test.

## Appendix auction, not the result

`forfeit_auction` records a two-bid forfeit contest for the course appendix. The higher integer bid becomes the Promiser. The forfeit written on the misaligned Break cell is the second bid. Similarity cannot change a bid or break a tie. A second bid above 4 makes Keep strictly better. A second bid below 4 makes Break strictly better. A second bid of exactly 4 leaves the Promiser indifferent, so there is no unique equilibrium. The function does not claim that bidding one's cost is a dominant strategy: a Promiser who Keeps does not pay the forfeit.

## Files

| File | Purpose |
|---|---|
| `trust_forfeit.py` | Matrices, Nashpy check, 12-round schedule, PS1 replay, auction record, CSV summary |
| `PS2_trust_forfeit.ipynb` | Colab notebook with saved output |
| `tests/test_trust_forfeit.py` | Equilibria, deviations, seed 206, and JavaScript parity |
| `tools/build_notebook.py` | Rebuilds the notebook from `trust_forfeit.py` |
| `outputs/results.json` | Saved run |

## Limits

Illustrative points. The Promiser's Keep and Break payoffs do not depend on whether the Decider trusted. Twelve rounds deal a fresh card and do not carry points into the next card. This is not a reputation model. `n = 0` for human play.

## License

MIT. See `LICENSE`.
