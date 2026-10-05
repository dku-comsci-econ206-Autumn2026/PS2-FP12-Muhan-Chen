"""Checks for the three matrices, Nashpy, the PS1 seed, and the JavaScript game."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import trust_forfeit as tf  # noqa: E402

HF = ROOT / "hf_static"


class MatrixTests(unittest.TestCase):
    def test_p_star(self):
        self.assertAlmostEqual(tf.p_star(), 0.6)

    def test_forfeit_is_not_paid_to_the_decider(self):
        self.assertEqual(tf.decider_payoff("trust", "break"), -4)
        self.assertEqual(tf.promiser_payoff("misaligned", "break", True), 5)
        self.assertEqual(tf.round_payoffs("misaligned", True, "break", "trust"), (-4, 5))

    def test_similarity_is_not_in_the_payoff(self):
        same = tf.round_payoffs("misaligned", False, "break", "trust")
        self.assertEqual(same, (-4, 10))

    def test_three_unique_equilibria(self):
        rows = { (r["alignment"], r["forfeit"]): r for r in tf.treatments() }
        self.assertEqual(rows[("aligned", False)]["equilibrium"], {"decider": "trust", "promiser": "keep"})
        self.assertEqual(rows[("misaligned", False)]["equilibrium"], {"decider": "verify", "promiser": "break"})
        self.assertEqual(rows[("misaligned", True)]["equilibrium"], {"decider": "trust", "promiser": "keep"})

    def test_nashpy_matches_the_scan(self):
        for alignment, forfeit in (("aligned", False), ("misaligned", False), ("misaligned", True)):
            decider, promiser = tf.matrices(alignment, forfeit)
            self.assertEqual(tf.pure_nash_scan(decider, promiser), tf.pure_nash_nashpy(decider, promiser))

    def test_deviations(self):
        # Misaligned, no forfeit: equilibrium is verify, break. Payoffs 2 and 10.
        self.assertLess(tf.promiser_payoff("misaligned", "keep", False), 10)
        self.assertLess(tf.decider_payoff("trust", "break"), 2)
        # Forfeit 5: equilibrium is trust, keep. Payoffs 6 and 6.
        self.assertLess(tf.promiser_payoff("misaligned", "break", True), 6)
        self.assertLess(tf.decider_payoff("verify", "keep"), 6)

    def test_aligned_card_rejects_a_forfeit(self):
        with self.assertRaises(ValueError):
            tf.promiser_payoff("aligned", "break", True)

    def test_ps1_seed_206(self):
        self.assertEqual(
            tf.ps1_replay(206),
            {"benchmark": 48, "always_verify": 24, "always_trust": 22, "similarity": 18},
        )

    def test_schedule_is_balanced(self):
        rounds = tf.build_rounds(206)
        self.assertEqual(len(rounds), 12)
        counts = tf._count_schedule(rounds)
        self.assertEqual(counts["aligned|same|forfeit=0"], 2)
        self.assertEqual(counts["aligned|different|forfeit=0"], 2)
        self.assertEqual(counts["misaligned|same|forfeit=0"], 2)
        self.assertEqual(counts["misaligned|different|forfeit=0"], 2)
        self.assertEqual(counts["misaligned|same|forfeit=1"], 2)
        self.assertEqual(counts["misaligned|different|forfeit=1"], 2)
        self.assertNotIn("aligned|same|forfeit=1", counts)

    def test_session_code(self):
        self.assertEqual(tf.session_seed("206"), 206)
        self.assertEqual(tf.session_seed(" 206 "), 206)
        self.assertEqual(tf.session_seed("fp12"), tf.session_seed("fp12"))
        self.assertNotEqual(tf.session_seed("fp12"), tf.session_seed("FP12"))

    def test_auction_does_not_use_similarity(self):
        a = tf.forfeit_auction((8, 3), (True, False), 206)
        b = tf.forfeit_auction((8, 3), (False, True), 206)
        self.assertEqual(a["winner"], b["winner"])
        self.assertEqual(a["forfeit"], 3)
        self.assertEqual(a["equilibrium"], {"decider": "verify", "promiser": "break"})
        high = tf.forfeit_auction((9, 6), (True, False), 206)
        self.assertEqual(high["equilibrium"], {"decider": "trust", "promiser": "keep"})
        tie_a = tf.forfeit_auction((5, 5), (True, False), 206)
        tie_b = tf.forfeit_auction((5, 5), (False, True), 206)
        self.assertEqual(tie_a["winner"], tie_b["winner"])
        self.assertEqual(tie_a["equilibrium"], {"decider": "trust", "promiser": "keep"})
        flat = tf.forfeit_auction((4, 4), (True, False), 206)
        self.assertFalse(flat["unique"])
        self.assertIsNone(flat["equilibrium"])

    def test_javascript_matches_python(self):
        script = HF / "verify_logic.js"
        raw = subprocess.check_output(["node", str(script)], text=True)
        payload = json.loads(raw)
        self.assertEqual(payload["rounds"], _public_rounds(tf.build_rounds(206)))
        self.assertEqual(payload["p_star"], 0.6)
        self.assertEqual(payload["payoff"], [-4, 5])
        self.assertEqual(payload["seed_code"], 206)
        self.assertEqual(payload["word_code"], tf.session_seed("fp12"))


def _public_rounds(rounds: list[dict]) -> list[dict]:
    return [
        {
            "alignment": rnd["alignment"],
            "similar": rnd["similar"],
            "forfeit": rnd["forfeit"],
            "ne_decider": rnd["ne_decider"],
            "ne_promiser": rnd["ne_promiser"],
        }
        for rnd in rounds
    ]


if __name__ == "__main__":
    unittest.main()
