/* node verify_logic.js — prints JSON for the Python parity test. */
const path = require("path");
const api = require(path.join(__dirname, "game_logic.js"));

const rounds = api.buildRounds(206);
const counts = {};
rounds.forEach(function (rnd) {
  const key = rnd.alignment + "|" + (rnd.similar ? "same" : "different") + "|forfeit=" + (rnd.forfeit ? 1 : 0);
  counts[key] = (counts[key] || 0) + 1;
});
const needed = [
  "aligned|same|forfeit=0",
  "aligned|different|forfeit=0",
  "misaligned|same|forfeit=0",
  "misaligned|different|forfeit=0",
  "misaligned|same|forfeit=1",
  "misaligned|different|forfeit=1",
];
needed.forEach(function (key) {
  if (counts[key] !== 2) throw new Error("bad count " + key + "=" + counts[key]);
});
if (rounds.length !== 12) throw new Error("expected 12 rounds");
if (api.deciderPayoff("trust", "break") !== -4) throw new Error("forfeit leaked to the decider");
if (api.promiserPayoff("misaligned", "break", true) !== 5) throw new Error("forfeit");
if (api.equilibrium("misaligned", false).decider !== "verify") throw new Error("baseline equilibrium");
if (api.equilibrium("misaligned", true).promiser !== "keep") throw new Error("forfeit equilibrium");

process.stdout.write(JSON.stringify({
  rounds: rounds,
  p_star: api.pStar,
  payoff: [api.deciderPayoff("trust", "break"), api.promiserPayoff("misaligned", "break", true)],
  seed_code: api.sessionSeed("206"),
  word_code: api.sessionSeed("fp12"),
}));
