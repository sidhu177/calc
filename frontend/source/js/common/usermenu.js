// @ts-check
/* global document */

function enableUsermenu() {
  const menu = document.querySelector('#usermenu');
  const trigger = document.querySelector('#usermenu .usermenu-trigger');
  const openLabel = 'Show user menu';
  const closeLabel = 'Close user menu';

  if (!menu || !trigger) {
    return;
  }

  trigger.setAttribute('aria-haspopup', true.toString());
  trigger.setAttribute('aria-expanded', false.toString());
  trigger.setAttribute('aria-label', openLabel);

  trigger.addEventListener('click', (e) => {
    menu.classList.toggle('is-open');
    const isOpen = menu.classList.contains('is-open');
    trigger.setAttribute('aria-expanded', isOpen.toString());
    trigger.setAttribute('aria-label', isOpen ? closeLabel : openLabel);
    e.preventDefault();
  });
}

document.addEventListener('DOMContentLoaded', enableUsermenu);
