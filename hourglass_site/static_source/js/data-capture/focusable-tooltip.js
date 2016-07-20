/* global jQuery, document */

const $ = jQuery;

$.fn.focusableTooltipify = function focusableTooltipify() {
  this.tooltipster({
    functionInit: function functionInit() {
      return $(this).attr('aria-label');
    },
  }).on('focus', function onFocus() {
    $(this).tooltipster('show');
  }).on('blur', function onBlur() {
    $(this).tooltipster('hide');
  });

  return this;
};

$(document).ready(() => {
  $('[data-focusable-tooltip]').focusableTooltipify();
});
