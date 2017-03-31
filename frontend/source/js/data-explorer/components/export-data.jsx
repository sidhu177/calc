import * as qs from "querystring";

import React from "react";
import { connect } from "react-redux";

import { getRatesParameters } from "../rates-request";

import { API_RATES_CSV } from "../constants";

export function ExportData({ querystring }) {
  const href = API_RATES_CSV + querystring;

  return (
    <a
      className="button button-primary export-data"
      title="Click to export your search results to an Excel file (CSV)"
      href={href}
    >
      ⬇ Export Data (CSV)
    </a>
  );
}

ExportData.propTypes = {
  querystring: React.PropTypes.string.isRequired
};

function mapStateToProps(state) {
  return {
    querystring: `?${qs.stringify(getRatesParameters(state))}`
  };
}

export default connect(mapStateToProps)(ExportData);
