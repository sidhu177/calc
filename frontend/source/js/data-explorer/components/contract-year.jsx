import React from "react";
import { connect } from "react-redux";

import Tooltip from "./tooltip";
import { setContractYear as setContractYearAction } from "../actions";
import {
  CONTRACT_YEAR_CURRENT,
  CONTRACT_YEAR_1,
  CONTRACT_YEAR_2,
  CONTRACT_YEAR_LABELS
} from "../constants";

const YEAR_LI_INFO = {
  [CONTRACT_YEAR_CURRENT]: {
    className: "contract-current-year-span checkbox-focus",
    shortLabel: "Current",
    idSuffix: "current-year"
  },
  [CONTRACT_YEAR_1]: {
    className: "checkbox-focus",
    shortLabel: "+1",
    idSuffix: "one-year-out"
  },
  [CONTRACT_YEAR_2]: {
    className: "contract-last-year-span checkbox-focus",
    shortLabel: "+2",
    idSuffix: "two-years-out"
  }
};

const TOOLTIP = "All five years of pricing are available in the export.";

export function ContractYear({ idPrefix, contractYear, setContractYear }) {
  const listItem = year => {
    const { className, shortLabel, idSuffix } = YEAR_LI_INFO[year];
    const id = `${idPrefix}${idSuffix}`;

    return (
      <li className="contract-list-item">
        <label htmlFor={id} className="radio">
          <input
            id={id}
            type="radio"
            checked={contractYear === year}
            onChange={() => {
              setContractYear(year);
            }}
            name="contract-year"
            value={year}
            tabIndex="0"
          />
          <span tabIndex="-1" className={className} aria-hidden="true">
            {shortLabel}
          </span>
          <span className="sr-only">
            {CONTRACT_YEAR_LABELS[year]}
          </span>
        </label>
      </li>
    );
  };

  return (
    <div className="filter contract-year">
      <fieldset className="fieldset-inputs">

        <legend>Contract year:</legend>

        <span className="filter-more-info">
          <Tooltip text={TOOLTIP}>
            <a
              href=""
              aria-label={TOOLTIP}
              onClick={e => {
                e.preventDefault();
              }}
            >
              What's this?
            </a>
          </Tooltip>
        </span>

        <h3 className="sr-only">Contract Year</h3>

        <ul className="contract-year-block">
          {listItem(CONTRACT_YEAR_CURRENT)}
          {listItem(CONTRACT_YEAR_1)}
          {listItem(CONTRACT_YEAR_2)}
        </ul>
      </fieldset>
    </div>
  );
}

ContractYear.propTypes = {
  contractYear: React.PropTypes.string.isRequired,
  setContractYear: React.PropTypes.func.isRequired,
  idPrefix: React.PropTypes.string
};

ContractYear.defaultProps = {
  idPrefix: ""
};

export default connect(state => ({ contractYear: state["contract-year"] }), {
  setContractYear: setContractYearAction
})(ContractYear);
