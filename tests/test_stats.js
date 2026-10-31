const assert = require('assert');
const stats = require('../site/stats-core.js');

function row(day, weight) {
  return { t: Date.parse(day + 'T00:00:00Z'), w: weight };
}

let rows = stats.withAverage([
  row('2026-10-27', 68.0), row('2026-10-28', 67.8),
  row('2026-10-29', 67.9), row('2026-10-30', 67.9),
], 7);
assert.strictEqual(rows[3].n, 4);
assert.strictEqual(stats.goalReached(rows, 68, 4), true);

rows = stats.withAverage([
  row('2026-10-27', 68.2), row('2026-10-28', 68.1),
  row('2026-10-29', 68.0), row('2026-10-30', 68.1),
], 7);
assert.strictEqual(stats.goalReached(rows, 68, 4), false);

rows = stats.withAverage([
  row('2026-10-28', 67.8), row('2026-10-29', 67.9), row('2026-10-30', 67.9),
], 7);
assert.strictEqual(stats.goalReached(rows, 68, 4), null);
assert.strictEqual(stats.pointLabel(Date.parse('2026-10-31T00:00:00Z'), 74.6), '31.10.2026 · 74,6 кг');

console.log('stats-core tests passed');
