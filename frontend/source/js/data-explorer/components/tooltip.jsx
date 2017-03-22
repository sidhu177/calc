/* global $ */

import React from 'react';

import { autobind } from '../util';

export default class Tooltip extends React.Component {
  constructor(props) {
    super(props);
    autobind(this, ['show', 'hide']);
  }

  componentDidMount() {
    if (!this.el) return;
    $(this.el)
      .tooltipster({})
      .tooltipster('content', this.props.text);
    this.el.addEventListener('focus', this.show, true);
    this.el.addEventListener('blur', this.hide, true);
    this.syncShowProp();
  }

  componentDidUpdate(prevProps) {
    if (!this.el) return;
    if (this.props.text !== prevProps.text) {
      $(this.el).tooltipster('content', this.props.text);
    }
    this.syncShowProp();
  }

  componentWillUnmount() {
    if (!this.el) return;
    $(this.el).tooltipster('destroy');
    this.el.removeEventListener('focus', this.show, true);
    this.el.removeEventListener('blur', this.hide, true);
  }

  show() {
    $(this.el).tooltipster('show');
  }

  hide() {
    $(this.el).tooltipster('hide');
  }

  syncShowProp() {
    if (typeof this.props.show !== 'boolean') {
      return;
    }

    const isHidden = $(this.el).tooltipster('status') === 'hidden';

    if (this.props.show && isHidden) {
      this.show();
    } else if (!this.props.show && !isHidden) {
      this.hide();
    }
  }

  render() {
    return (
      <span ref={(el) => { this.el = el; }}>
        {this.props.children}
      </span>
    );
  }
}

Tooltip.propTypes = {
  children: React.PropTypes.any,
  text: React.PropTypes.string.isRequired,
  show: React.PropTypes.bool,
};

Tooltip.defaultProps = {
  children: null,
  show: false,
};
