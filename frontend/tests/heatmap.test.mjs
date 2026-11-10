import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { parseHeatmap, cellFeatures, scoreColor } from "../src/heatmap.ts";

const fixture = JSON.parse(
  readFileSync(new URL("../public/mock-heatmap.json", import.meta.url), "utf8"),
);

test("all 80 cells form aligned closed polygons in longitude/latitude order", () => {
  const data = parseHeatmap(fixture);
  assert.equal(data.cells.length, 80);
  const collection = cellFeatures(data.cells);
  for (const feature of collection.features) {
    const ring = feature.geometry.coordinates[0];
    assert.equal(ring.length, 5);
    assert.deepEqual(ring[0], ring[4]);
    assert.ok(ring[0][0] > 77 && ring[0][1] > 13);
  }
});

test("legend colours use fixed boundaries", () => {
  assert.deepEqual(scoreColor(0), scoreColor(0.329));
  assert.notDeepEqual(scoreColor(0.329), scoreColor(0.33));
  assert.deepEqual(scoreColor(0.33), scoreColor(0.659));
  assert.deepEqual(scoreColor(0.66), scoreColor(1));
});

test("rejects unsafe scores, duplicate IDs, and swapped coordinates", () => {
  for (const mutate of [
    (d) => (d.cells[0].score = 2),
    (d) => (d.cells[0].score = NaN),
    (d) => (d.cells[1].id = d.cells[0].id),
    (d) => d.cells[0].bounds.reverse(),
    (d) => (d.is_mock = false),
    (d) => d.cells.pop(),
  ]) {
    const data = structuredClone(fixture);
    mutate(data);
    assert.throws(() => parseHeatmap(data));
  }
});

test("filter extremes show all or no cells without changing the fixture", () => {
  const data = parseHeatmap(fixture);
  assert.equal(data.cells.filter((c) => c.score >= 0).length, 80);
  assert.equal(data.cells.filter((c) => c.score >= 1).length, 0);
  const high = data.cells.filter((c) => c.score >= 0.66);
  assert.ok(high.length > 0 && high.length < 80);
  assert.equal(data.cells.length, 80);
});
