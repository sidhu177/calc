/* global QUnit window */

import ga from "../common/ga";

QUnit.module("ga", {
  beforeEach() {
    delete window.ga;
  },
  afterEach() {
    delete window.ga;
  }
});

QUnit.test("ga does not throw when window.ga is undefined", assert => {
  ga();
  assert.ok(true, "calling ga() does not throw");
});

QUnit.test("ga calls window.ga when it is a function", assert => {
  window.ga = (...args) => {
    assert.deepEqual(args, [1, 2, 3]);
  };
  ga(1, 2, 3);
});
