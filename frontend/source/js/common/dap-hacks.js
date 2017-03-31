/* global window */

export const IS_SUPPORTED = "MutationObserver" in window;

const DEFAULT_INIT_AUTO_TRACKER_NAME = "_initAutoTracker";

/**
 * Here we notify DAP about new links we've added to the page, so that
 * it can auto-track them. For more background, see:
 *
 *   https://github.com/digital-analytics-program/gov-wide-code/pull/47
 */

export function findLinksInNodeList(list) {
  const links = [];

  for (let i = 0; i < list.length; i++) {
    const node = list[i];

    if (node.nodeType === node.ELEMENT_NODE) {
      const nodeName = node.nodeName && node.nodeName.toLowerCase();

      if (nodeName === "a") {
        links.push(node);
      } else {
        const innerLinks = node.querySelectorAll("a");
        for (let j = 0; j < innerLinks.length; j++) {
          links.push(innerLinks[i]);
        }
      }
    }
  }

  return links;
}

/**
 * Well, this is horrible.
 *
 * To work around DAP's `_initAutoTracker()` getting *all* the links on
 * a page and adding event handlers to them--which is a problem because
 * it can lead to the same link being tracked multiple times--we will
 * temporarily "hack" the underlying DOM API being used to only give the
 * auto tracker the links we know aren't currently being tracked.
 *
 * For more details on a hopefully better workaround in the future,
 * see:
 *
 *   https://github.com/digital-analytics-program/gov-wide-code/pull/48
 */

export function hackilyNotifyAutoTrackerOfNewLinks(initAutoTracker, links) {
  const oldGet = window.document.getElementsByTagName;

  window.document.getElementsByTagName = () => links;

  try {
    initAutoTracker();
  } finally {
    window.document.getElementsByTagName = oldGet;
  }
}

export function observe(
  parentEl = window.document.documentElement,
  getInitAutoTracker = () => window[DEFAULT_INIT_AUTO_TRACKER_NAME]
) {
  const observer = new window.MutationObserver(mutations => {
    const initAutoTracker = getInitAutoTracker();

    if (
      window.document.readyState === "loading" ||
      typeof initAutoTracker !== "function"
    ) {
      // DAP hasn't been loaded or initialized the auto tracker yet.
      // Once that happens, it'll find any links that were added as a
      // result of these particular mutations, so we can just leave now.
      return;
    }

    const links = mutations
      .map(mut => findLinksInNodeList(mut.addedNodes))
      .reduce((a, b) => a.concat(b), []);

    if (links.length) {
      hackilyNotifyAutoTrackerOfNewLinks(initAutoTracker, links);
    }
  });

  observer.observe(parentEl, {
    childList: true,
    subtree: true
  });

  return observer;
}

if (IS_SUPPORTED) {
  observe();
}
