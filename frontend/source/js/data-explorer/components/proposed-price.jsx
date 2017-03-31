import React from "react";
import { connect } from "react-redux";

import { setProposedPrice } from "../actions";

export class ProposedPrice extends React.Component {
  static handleGoClick(e) {
    // Don't do anything for now; the legacy front-end caused the
    // proposed price to be displayed on this histogram when this was
    // clicked, but since we do that on a per-keystroke basis, there's
    // no need to do it here. At the same time, though, we're concerned
    // that removing the "Go" button could make things even more confusing
    // than they already are, so for now we'll do a no-op.
    //
    // Note also that we *do* need to prevent the default behavior here, or
    // else the form will be submitted.
    e.preventDefault();
  }

  constructor(props) {
    super(props);
    this.state = { typed: this.props.proposedPrice || "" };
    this.handleChange = this.handleChange.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.proposedPrice !== this.props.proposedPrice) {
      const typedFloat = parseFloat(this.state.typed || "0");
      if (typedFloat !== nextProps.proposedPrice) {
        this.setState({ typed: nextProps.proposedPrice || "" });
      }
    }
  }

  componentDidUpdate(_, prevState) {
    if (prevState.typed !== this.state.typed) {
      const value = this.state.typed;
      const floatValue = value ? parseFloat(value) : 0;
      if (!isNaN(floatValue) && floatValue >= 0) {
        this.props.setProposedPrice(floatValue);
      }
    }
  }

  handleChange(e) {
    const value = e.target.value;
    const filteredChars = [];
    let decimalFound = false;
    let centDigits = 0;

    for (let i = 0; i < value.length; i++) {
      const c = value[i];

      if (/[0-9]/.test(c) && centDigits < 2) {
        filteredChars.push(c);
        if (decimalFound) {
          centDigits++;
        }
      } else if (c === "." && !decimalFound) {
        filteredChars.push(c);
        decimalFound = true;
      }
    }

    this.setState({ typed: filteredChars.join("") });
  }

  render() {
    // Note that Chrome has issues with number input, so we're just
    // going to use a standard text field here. This is unfortunate for
    // mobile users, since they won't get a numeric keypad.
    //
    // See more details at: https://github.com/facebook/react/issues/1549

    const id = `${this.props.idPrefix}proposed-price`;

    return (
      <div className="proposed-price">
        <label htmlFor={id} className="sr-only">Proposed price</label>
        <input
          id={id}
          type="text"
          name="proposed-price"
          className="form__inline"
          placeholder="Proposed price"
          value={this.state.typed}
          onChange={this.handleChange}
        />
        <button
          className="button-primary go"
          onClick={ProposedPrice.handleGoClick}
        >
          Go
        </button>
      </div>
    );
  }
}

ProposedPrice.propTypes = {
  proposedPrice: React.PropTypes.number.isRequired,
  setProposedPrice: React.PropTypes.func.isRequired,
  idPrefix: React.PropTypes.string
};

ProposedPrice.defaultProps = {
  idPrefix: ""
};

export default connect(state => ({ proposedPrice: state["proposed-price"] }), {
  setProposedPrice
})(ProposedPrice);
