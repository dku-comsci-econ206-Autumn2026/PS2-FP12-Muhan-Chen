/* Shared rules for the two-player game. The computer deals cards. It does not choose. */
(function (root, factory) {
  const api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.TrustForfeit = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  const FORFEIT = 5;
  const N_ROUNDS = 12;
  const PRIORITIES = ["cost", "speed", "equity"];
  const PRIORITY_LABEL = {
    cost: "cost-efficiency first",
    speed: "delivery-speed first",
    equity: "supplier-equity first",
  };

  function i32(x) {
    x = x | 0;
    return x;
  }

  function mulberry32(seed) {
    let a = seed | 0;
    return function () {
      a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function sessionSeed(code) {
    const text = String(code).trim();
    if (!text) throw new Error("session code is empty");
    if (/^\d+$/.test(text)) return Number(text) >>> 0;
    let h = 2166136261;
    for (let i = 0; i < text.length; i++) {
      h ^= text.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  function shuffle(items, rng) {
    const out = items.slice();
    for (let i = out.length - 1; i > 0; i--) {
      const j = Math.floor(rng() * (i + 1));
      const tmp = out[i];
      out[i] = out[j];
      out[j] = tmp;
    }
    return out;
  }

  function promiserPayoff(alignment, action, forfeit) {
    if (alignment === "aligned" && forfeit) throw new Error("an aligned card has no forfeit");
    const gross = alignment === "aligned"
      ? (action === "keep" ? 6 : 3)
      : (action === "keep" ? 6 : 10);
    return forfeit && action === "break" ? gross - FORFEIT : gross;
  }

  function deciderPayoff(decider, promiser) {
    if (decider === "verify") return 2;
    return promiser === "keep" ? 6 : -4;
  }

  function equilibrium(alignment, forfeit) {
    if (alignment === "aligned" || forfeit) return { decider: "trust", promiser: "keep" };
    return { decider: "verify", promiser: "break" };
  }

  function buildRounds(seed) {
    const cells = [];
    for (const alignment of ["aligned", "misaligned"]) {
      for (const similar of [true, false]) {
        const forfeits = alignment === "aligned" ? [false] : [false, true];
        for (const forfeit of forfeits) {
          for (let k = 0; k < 2; k++) cells.push({ alignment, similar, forfeit });
        }
      }
    }
    return shuffle(cells, mulberry32(seed)).map(function (cell) {
      const ne = equilibrium(cell.alignment, cell.forfeit);
      return {
        alignment: cell.alignment,
        similar: cell.similar,
        forfeit: cell.forfeit,
        ne_decider: ne.decider,
        ne_promiser: ne.promiser,
      };
    });
  }

  function shownPriority(deciderPriority, similar) {
    const i = PRIORITIES.indexOf(deciderPriority);
    if (i < 0) throw new Error(deciderPriority);
    return similar ? deciderPriority : PRIORITIES[(i + 1) % PRIORITIES.length];
  }

  return {
    FORFEIT: FORFEIT,
    N_ROUNDS: N_ROUNDS,
    PRIORITIES: PRIORITIES,
    PRIORITY_LABEL: PRIORITY_LABEL,
    pStar: 0.6,
    sessionSeed: sessionSeed,
    buildRounds: buildRounds,
    promiserPayoff: promiserPayoff,
    deciderPayoff: deciderPayoff,
    equilibrium: equilibrium,
    shownPriority: shownPriority,
    i32: i32,
  };
});
