/* global QUnit window document */

import {
  IS_SUPPORTED,
  findLinksInNodeList,
  observe,
  hackilyNotifyAutoTrackerOfNewLinks
} from "../common/dap-hacks";

QUnit.module("dap-hacks");

QUnit.test("findLinksInNodeList() finds top-level links", assert => {
  const a = document.createElement("a");
  const links = findLinksInNodeList([a]);

  assert.equal(links.length, 1);
  assert.strictEqual(links[0], a);
});

QUnit.test("findLinksInNodeList() finds inner links", assert => {
  const div = document.createElement("div");

  div.innerHTML = '<p>hello <a href="http://boop">there</a></p>';

  const links = findLinksInNodeList([div]);

  assert.equal(links.length, 1);
  assert.equal(links[0].getAttribute("href"), "http://boop");
});

QUnit.test("hack horribly hacks getElementsByTagName()", assert => {
  const originalGebtn = document.getElementsByTagName;
  const links = [1, 2, 3];
  hackilyNotifyAutoTrackerOfNewLinks(
    () => {
      assert.strictEqual(document.getElementsByTagName("a"), links);
    },
    links
  );
  assert.strictEqual(document.getElementsByTagName, originalGebtn);
});

QUnit.test("hack restores getElementsByTagName() on err", assert => {
  const originalGebtn = document.getElementsByTagName;
  const kaboom = new Error();

  try {
    hackilyNotifyAutoTrackerOfNewLinks(
      () => {
        throw kaboom;
      },
      []
    );
  } catch (e) {
    assert.strictEqual(e, kaboom);
    assert.strictEqual(document.getElementsByTagName, originalGebtn);
  }
});

function advancedTest(name, cb) {
  if (!IS_SUPPORTED) {
    QUnit.skip(name, cb);
  } else {
    QUnit.test(name, cb);
  }
}

advancedTest("observe() works", assert => {
  const div = document.createElement("div");
  const done = assert.async();
  const a = document.createElement("a");
  const initAutoTracker = () => {
    const elementsFound = document.getElementsByTagName("a");
    assert.equal(elementsFound.length, 1);
    assert.strictEqual(elementsFound[0], a);
    window.setTimeout(
      () => {
        document.body.removeChild(div);
        done();
      },
      1
    );
  };

  div.innerHTML = '<a href="http://foo">foo</a>';
  document.body.appendChild(div);
  observe(div, () => initAutoTracker);
  div.appendChild(a);
});
