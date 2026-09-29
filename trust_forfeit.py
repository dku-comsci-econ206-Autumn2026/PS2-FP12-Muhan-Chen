"""Trust the table, not the resemblance.

Two human players. The computer deals a public payoff card and a similarity
label, then hides each choice until both are locked. It never plays.

Decider: Trust+Keep 6, Trust+Break -4, Verify 2. So Trust is as good as
Verify only when the Promiser keeps with probability at least p* = 0.6.

Promiser payoffs do not depend on Trust versus Verify:
  aligned:    Keep 6, Break 3
  misaligned: Keep 6, Break 10
A misaligned Break loses a forfeit of 5, so Break pays 5. The forfeit is
not given to the Decider.

The similarity label (SAME / DIFFERENT) changes no payoff and cannot waive
the forfeit.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import nashpy
import numpy as np

FORFEIT = 5
P_STAR = 0.6
N_ROUNDS = 12
SEED = 206
PRIORITIES = ("cost", "speed", "equity")
ALIGNMENTS = ("aligned", "misaligned")
DECIDER_ACTIONS = ("trust", "verify")
PROMISER_ACTIONS = ("keep", "break")

# Decider payoffs. The forfeit is not added here.
DECIDER_PAY = {("trust", "keep"): 6, ("trust", "break"): -4, ("verify", "keep"): 2, ("verify", "break"): 2}

# Promiser payoffs before any forfeit.
PROMISER_GROSS = {"aligned": {"keep": 6, "break": 3}, "misaligned": {"keep": 6, "break": 10}}

P_KEEP = {"aligned": 0.85, "misaligned": 0.25}
P_EXPLICIT = 0.9
EXPLICIT_MSGS = (
    "I commit to the fair split this round. You can count on it.",
    "I will honour the agreed allocation in full — no deviation.",
    "My promise: I cooperate this round, exactly as specified.",
    "I guarantee I will keep to the agreed terms.",
)
HEDGED_MSGS = (
    "I intend to work with you, subject to my constraints this round.",
    "I will try to accommodate the agreed allocation where feasible.",
)


def p_star() -> float:
    """Trust matches Verify when 10p - 4 = 2."""
    trust_keep = DECIDER_PAY[("trust", "keep")]
    trust_break = DECIDER_PAY[("trust", "break")]
    verify = DECIDER_PAY[("verify", "keep")]
    return (verify - trust_break) / (trust_keep - trust_break)


def promiser_payoff(alignment: str, action: str, forfeit: bool) -> int:
    if alignment not in PROMISER_GROSS or action not in PROMISER_ACTIONS:
        raise ValueError(f"bad promiser input: {alignment}, {action}")
    if alignment == "aligned" and forfeit:
        raise ValueError("an aligned card has no forfeit")
    gross = PROMISER_GROSS[alignment][action]
    if forfeit and action == "break":
        return gross - FORFEIT
    return gross


def decider_payoff(decider: str, promiser: str) -> int:
    key = (decider, promiser)
    if key not in DECIDER_PAY:
        raise ValueError(f"bad decider input: {decider}, {promiser}")
    return DECIDER_PAY[key]


def round_payoffs(alignment: str, forfeit: bool, promiser: str, decider: str) -> tuple[int, int]:
    """Return (decider points, promiser points)."""
    return decider_payoff(decider, promiser), promiser_payoff(alignment, promiser, forfeit)


def matrices(alignment: str, forfeit: bool) -> tuple[np.ndarray, np.ndarray]:
    """Rows are Trust, Verify. Columns are Keep, Break."""
    decider = np.zeros((2, 2))
    promiser = np.zeros((2, 2))
    for i, d_act in enumerate(DECIDER_ACTIONS):
        for j, p_act in enumerate(PROMISER_ACTIONS):
            decider[i, j], promiser[i, j] = round_payoffs(alignment, forfeit, p_act, d_act)
    return decider, promiser


def pure_nash_scan(decider: np.ndarray, promiser: np.ndarray) -> list[tuple[str, str]]:
    """Pure Nash equilibria: neither player gains by switching."""
    found = []
    for i, d_act in enumerate(DECIDER_ACTIONS):
        for j, p_act in enumerate(PROMISER_ACTIONS):
            decider_ok = decider[i, j] + 1e-9 >= decider[1 - i, j]
            promiser_ok = promiser[i, j] + 1e-9 >= promiser[i, 1 - j]
            if decider_ok and promiser_ok:
                found.append((d_act, p_act))
    return found


def pure_nash_nashpy(decider: np.ndarray, promiser: np.ndarray) -> list[tuple[str, str]]:
    game = nashpy.Game(decider, promiser)
    found = []
    for sigma_r, sigma_c in game.support_enumeration():
        if float(np.max(sigma_r)) >= 1 - 1e-8 and float(np.max(sigma_c)) >= 1 - 1e-8:
            found.append(
                (DECIDER_ACTIONS[int(np.argmax(sigma_r))], PROMISER_ACTIONS[int(np.argmax(sigma_c))])
            )
    return sorted(set(found))


def equilibrium(alignment: str, forfeit: bool) -> tuple[str, str]:
    """Unique pure Nash equilibrium selected by strict dominance."""
    decider, promiser = matrices(alignment, forfeit)
    scan = pure_nash_scan(decider, promiser)
    packaged = pure_nash_nashpy(decider, promiser)
    if scan != packaged:
        raise RuntimeError(f"Nashpy {packaged} does not match the matrix scan {scan}")
    if len(scan) != 1:
        raise RuntimeError(f"expected one pure equilibrium, found {scan}")
    return scan[0]


def treatments() -> list[dict]:
    specs = [
        ("aligned", False, ("trust", "keep"), (6, 6)),
        ("misaligned", False, ("verify", "break"), (2, 10)),
        ("misaligned", True, ("trust", "keep"), (6, 6)),
    ]
    rows = []
    for alignment, forfeit, expected, pay in specs:
        got = equilibrium(alignment, forfeit)
        if got != expected:
            raise RuntimeError(f"{alignment} forfeit={forfeit}: {got} != {expected}")
        d_pay, p_pay = round_payoffs(alignment, forfeit, expected[1], expected[0])
        if (d_pay, p_pay) != pay:
            raise RuntimeError(f"equilibrium payoffs {(d_pay, p_pay)} != {pay}")
        decider_m, promiser_m = matrices(alignment, forfeit)
        rows.append(
            {
                "alignment": alignment,
                "forfeit": forfeit,
                "equilibrium": {"decider": expected[0], "promiser": expected[1]},
                "equilibrium_payoffs": {"decider": pay[0], "promiser": pay[1]},
                "decider_matrix": decider_m.astype(int).tolist(),
                "promiser_matrix": promiser_m.astype(int).tolist(),
            }
        )
    return rows


def _i32(x: int) -> int:
    x &= 0xFFFFFFFF
    return x - 0x100000000 if x >= 0x80000000 else x


def _u32(x: int) -> int:
    return x & 0xFFFFFFFF


def mulberry32(seed: int):
    """JavaScript mulberry32. The same seed yields the same draws in [0, 1)."""
    state = [_i32(seed)]

    def rng() -> float:
        state[0] = _i32(state[0] + 0x6D2B79F5)
        a = state[0]
        t = _i32(_i32(a ^ (_u32(a) >> 15)) * _i32(1 | a))
        t = _i32(t + _i32(_i32(t ^ (_u32(t) >> 7)) * _i32(61 | t))) ^ t
        return _u32(t ^ (_u32(t) >> 14)) / 4294967296.0

    return rng


def session_seed(code: str) -> int:
    """A numeric session code is the seed. Any other code is an FNV-1a hash."""
    text = str(code).strip()
    if not text:
        raise ValueError("session code is empty")
    if text.isdigit():
        return int(text) & 0xFFFFFFFF
    h = 2166136261
    for ch in text:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def _shuffle(items: list, rng) -> list:
    out = list(items)
    for i in range(len(out) - 1, 0, -1):
        j = int(math.floor(rng() * (i + 1)))
        out[i], out[j] = out[j], out[i]
    return out


def build_rounds(seed: int) -> list[dict]:
    """Twelve public cards. Aligned rounds have no forfeit.

    Two of each: aligned × {same, different}, and misaligned × {same, different}
    × {forfeit, no forfeit}. The seed only shuffles this fixed list.
    """
    cells = []
    for alignment in ALIGNMENTS:
        for similar in (True, False):
            forfeits = (False,) if alignment == "aligned" else (False, True)
            for forfeit in forfeits:
                for _ in range(2):
                    cells.append({"alignment": alignment, "similar": similar, "forfeit": forfeit})
    if len(cells) != N_ROUNDS:
        raise RuntimeError(f"schedule has {len(cells)} rounds")
    rounds = []
    for cell in _shuffle(cells, mulberry32(seed)):
        decider_act, promiser_act = equilibrium(cell["alignment"], cell["forfeit"])
        cell = dict(cell)
        cell["ne_decider"] = decider_act
        cell["ne_promiser"] = promiser_act
        rounds.append(cell)
    return rounds


def shown_priority(decider_priority: str, similar: bool) -> str:
    if decider_priority not in PRIORITIES:
        raise ValueError(decider_priority)
    if similar:
        return decider_priority
    return PRIORITIES[(PRIORITIES.index(decider_priority) + 1) % len(PRIORITIES)]


def ps1_replay(seed: int = SEED) -> dict:
    """Replay the graded PS1 game. The agent keep/break draw is exogenous.

    This is a reproduction of the old schedule, not a player in the new game.
    """
    rng = mulberry32(seed)
    cells = [{"alignment": al, "similar": sim} for al in ALIGNMENTS for sim in (True, False) for _ in range(3)]
    cells = _shuffle(cells, rng)
    rounds = []
    for cell in cells:
        explicit = rng() < P_EXPLICIT
        kept = rng() < P_KEEP[cell["alignment"]]
        phrase = rng()
        pool = EXPLICIT_MSGS if explicit else HEDGED_MSGS
        rounds.append(
            {
                "alignment": cell["alignment"],
                "similar": cell["similar"],
                "explicit": explicit,
                "kept": kept,
                "message": pool[int(math.floor(phrase * len(pool)))],
            }
        )

    def total(choice) -> int:
        score = 0
        for rnd in rounds:
            if choice(rnd) == "trust":
                score += DECIDER_PAY[("trust", "keep" if rnd["kept"] else "break")]
            else:
                score += DECIDER_PAY[("verify", "keep")]
        return score

    policies = {
        "benchmark": lambda rnd: "trust" if rnd["alignment"] == "aligned" else "verify",
        "always_verify": lambda _rnd: "verify",
        "always_trust": lambda _rnd: "trust",
        "similarity": lambda rnd: "trust" if rnd["similar"] else "verify",
    }
    return {name: total(fn) for name, fn in policies.items()}


def forfeit_auction(bids: tuple[int, int], similar: tuple[bool, bool], seed: int) -> dict:
    """Appendix record only. Two sealed forfeit bids. This is not the paper's result.

    The higher bid becomes the Promiser. The forfeit that is written onto the
    misaligned Break cell is the second bid. Similarity cannot change a bid or
    break a tie. A tie uses the session seed, not the label.

    Keep still pays 6 and returns nothing extra. A second bid above 4 makes
    Keep strictly better (Break pays 10 minus that bid). A second bid below 4
    makes Break strictly better. A second bid of exactly 4 leaves the Promiser
    indifferent, so there is no unique equilibrium. Bidding-your-cost is not
    claimed: a player who Keeps does not pay the forfeit.
    """
    if len(bids) != 2 or len(similar) != 2:
        raise ValueError("need two bids and two similarity labels")
    if any(not isinstance(b, int) for b in bids):
        raise ValueError("bids are integers")
    if any(b < 0 for b in bids):
        raise ValueError("bids are nonnegative")
    order = sorted(range(2), key=lambda i: -bids[i])
    tied = bids[0] == bids[1]
    if tied:
        winner = 0 if mulberry32(seed)() < 0.5 else 1
    else:
        winner = order[0]
    second = min(bids)
    break_pay = 10 - second
    if second > 4:
        ne = ("trust", "keep")
        unique = True
    elif second < 4:
        ne = ("verify", "break")
        unique = True
    else:
        ne = None
        unique = False
    return {
        "winner": winner,
        "forfeit": second,
        "break_payoff": break_pay,
        "unique": unique,
        "equilibrium": None if ne is None else {"decider": ne[0], "promiser": ne[1]},
        "tie": tied,
        "similarity_ignored": True,
    }


def summarize_classroom(path: Path) -> dict:
    """Compare a Hugging Face CSV with the equilibrium of each round. n is the row count."""
    with Path(path).open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return {"n_rounds": 0, "n_sessions": 0}
    follow = 0
    for row in rows:
        ok = row["decider"] == row["ne_decider"] and row["promiser"] == row["ne_promiser"]
        follow += int(ok)
    sessions = {row["session"] for row in rows}
    return {
        "n_rounds": len(rows),
        "n_sessions": len(sessions),
        "rounds_matching_equilibrium": follow,
        "note": "Interface clicks are not this file unless a person exported the CSV.",
    }


def results() -> dict:
    totals = ps1_replay(SEED)
    expected = {"benchmark": 48, "always_verify": 24, "always_trust": 22, "similarity": 18}
    if totals != expected:
        raise RuntimeError(f"PS1 seed {SEED} totals {totals} != {expected}")
    if abs(p_star() - P_STAR) > 1e-12:
        raise RuntimeError("p* drifted")
    return {
        "p_star": P_STAR,
        "forfeit": FORFEIT,
        "forfeit_not_transferred": True,
        "similarity_changes_payoff": False,
        "treatments": treatments(),
        "ps1_seed_206": totals,
        "schedule_seed_206_counts": _count_schedule(build_rounds(SEED)),
        "auction_examples": [
            forfeit_auction((8, 3), (True, False), SEED),
            forfeit_auction((9, 6), (False, True), SEED),
            forfeit_auction((5, 5), (True, False), SEED),
            forfeit_auction((5, 5), (False, True), SEED),
        ],
        "human_n": 0,
    }


def _count_schedule(rounds: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for rnd in rounds:
        key = f"{rnd['alignment']}|{'same' if rnd['similar'] else 'different'}|forfeit={int(rnd['forfeit'])}"
        counts[key] = counts.get(key, 0) + 1
    return counts


def main() -> None:
    out = Path(__file__).resolve().parent / "outputs"
    out.mkdir(exist_ok=True)
    payload = results()
    (out / "results.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("p*", payload["p_star"])
    for row in payload["treatments"]:
        eq = row["equilibrium"]
        print(row["alignment"], "forfeit" if row["forfeit"] else "no forfeit", eq["decider"], eq["promiser"])
    print("PS1 seed 206", payload["ps1_seed_206"])


if __name__ == "__main__":
    main()