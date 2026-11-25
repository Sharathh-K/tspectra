import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { geometry } from '../src/layers/geometry.js';

test('rendered polygons use raster corner order and keep row-major labels', () => {
  const scene = JSON.parse(readFileSync(new URL('../public/mock/risk.json', import.meta.url)));
  const { boundary, cells } = geometry(scene);
  assert.equal(cells.length, scene.width * scene.height);
  assert.equal(boundary[0], scene.corners[0]);
  assert.equal(boundary[2], scene.corners.at(-1));
  for (const cell of cells) {
    assert.equal(cell.label, scene.labels[cell.row * scene.width + cell.col]);
    const n = cell.row * (scene.width + 1) + cell.col;
    const expected = [n, n+1, n+scene.width+2, n+scene.width+1].map(i => scene.corners[i]);
    assert.deepEqual(cell.polygon, expected);
    for (const axis of [0,1]) {
      assert.equal(cell.center[axis], expected.reduce((sum,p) => sum+p[axis],0)/4);
    }
  }
});
