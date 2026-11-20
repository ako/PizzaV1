import { test } from "node:test";
import assert from "node:assert/strict";
import { point, along, courierAt } from "../build-test/geo.mjs";

test("point rejects missing, 0/0 and out-of-range values", () => {
    assert.equal(point(undefined, 1), undefined);
    assert.equal(point(0, 0), undefined);
    assert.equal(point(95, 0), undefined);
    assert.equal(point(NaN, 2), undefined);
    assert.deepEqual(point(37.76, -122.41), [37.76, -122.41]);
});

test("along clamps to the segment", () => {
    assert.deepEqual(along([0, 0], [10, 20], 0.5), [5, 10]);
    assert.deepEqual(along([0, 0], [10, 20], -1), [0, 0]);
    assert.deepEqual(along([0, 0], [10, 20], 2), [10, 20]);
});

test("courier only with a route and progress >= 0", () => {
    const s = [37.76, -122.41], d = [37.79, -122.39];
    assert.equal(courierAt(s, undefined, 0.5), undefined);
    assert.equal(courierAt(s, d, -1), undefined);
    assert.deepEqual(courierAt(s, d, 1), d);
});
