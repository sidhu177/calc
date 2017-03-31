/* global window */

/**
 * This is just a wrapper around Google Analytics' ga() function, which
 * should be included inline at the top of the page. If it wasn't included
 * at the top of the page, however, we'll just no-op
 * so that code which calls it still works, allowing GA to be an optional
 * dependency.
 */

function ga(...args) {
  if (typeof window.ga === "function") {
    return window.ga.apply(this, args);
  }
  return undefined;
}

module.exports = ga;
