/* global window, document */
/* eslint no-alert: "off" */

class WebComponentLink extends window.HTMLAnchorElement {
  attachedCallback() {
    const tag = this.getAttribute('data-tag');
    const extendsClass = this.getAttribute('data-extends');
    let el;

    if (extendsClass) {
      el = document.createElement(tag, {
        is: extendsClass,
      });
    } else {
      el = document.createElement(tag);
    }

    const proto = Object.getPrototypeOf(el);

    if (!proto.SOURCE_FILENAME) {
      window.alert(
        `prototype for web component ${this.textContent} ` +
        'has no SOURCE_FILENAME property!',
      );
    }
    this.setAttribute('href', this.href + proto.SOURCE_FILENAME);
  }
}

document.registerElement('web-component-link', {
  extends: 'a',
  prototype: WebComponentLink.prototype,
});
