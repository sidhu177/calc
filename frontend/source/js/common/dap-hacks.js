// @ts-check
/* eslint-env browser */

export const IS_SUPPORTED = 'MutationObserver' in window;

/**
 * Here we notify DAP about new links we've added to the page, so that
 * it can auto-track them. For more background, see:
 *
 *   https://github.com/digital-analytics-program/gov-wide-code/pull/47
 */

/**
 * This returns all the <a> elements in a NodeList. It also searches
 * through the descendants of nodes in the list and returns them.
 *
 * @param {NodeList} list The list of nodes to filter/descend through.
 * @return {HTMLAnchorElement[]} The <a> elements in the list.
 */

export function findLinksInNodeList(list) {
  const links = [];

  for (let i = 0; i < list.length; i++) {
    const node = list[i];

    if (node instanceof HTMLElement) {
      if (node instanceof HTMLAnchorElement) {
        links.push(node);
      } else {
        const innerLinks = node.querySelectorAll('a');
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
 *
 * @param initAutoTracker {Function} A function that initializes DAP's
 *   auto-tracker, using `getElementsByTagName('a')` to return all the
 *   links on a page.
 * @param links {HTMLElement[]} The list of links which
 *   `getElementsByTagName()` will temporarily be monkeypatched to return.
 */

export function hackilyNotifyAutoTrackerOfNewLinks(initAutoTracker, links) {
  const oldGet = window.document.getElementsByTagName;

  // @ts-ignore   TypeScript, please forgive us for doing this.
  window.document.getElementsByTagName = () => links;

  try {
    initAutoTracker();
  } finally {
    window.document.getElementsByTagName = oldGet;
  }
}

/**
 * This function observes the document for mutations; whenever new links
 * are added, it lets DAP know about them, so that their clicks can
 * be tracked.
 *
 * @param {HTMLElement} parentEl The parent element to observe. Defaults
 *   to the topmost <html> element.
 * @param {Function} getInitAutoTracker A function that returns either DAP's
 *   private `_initAutoTracker` function, or `undefined` if DAP hasn't
 *   been loaded.
 */
export function observe(
  parentEl = window.document.documentElement,
  getInitAutoTracker = () => window._initAutoTracker, // eslint-disable-line no-underscore-dangle
) {
  const observer = new MutationObserver((mutations) => {
    const initAutoTracker = getInitAutoTracker();

    if (window.document.readyState === 'loading' ||
        typeof initAutoTracker !== 'function') {
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
    subtree: true,
  });

  return observer;
}

if (IS_SUPPORTED) {
  observe();
}
