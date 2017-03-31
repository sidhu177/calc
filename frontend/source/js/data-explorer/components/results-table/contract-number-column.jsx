import React from "react";

import createSortableColumn from "./sortable-column";

const DOCUMENT_SVG = (
  <svg className="document-icon" width="8" height="8" viewBox="0 0 8 8">
    <path
      d="M0 0v8h7v-4h-4v-4h-3zm4 0v3h3l-3-3zm-3 2h1v1h-1v-1zm0
             2h1v1h-1v-1zm0 2h4v1h-4v-1z"
    />
  </svg>
);

const column = createSortableColumn({
  key: "idv_piid",
  title: "Contract #",
  description: "Contract number"
});

export const HeaderCell = column.HeaderCell;

function createGsaAdvantageUrl(contractNumber) {
  const id = contractNumber.split("-").join("");

  return `https://www.gsaadvantage.gov/ref_text/${id}/${id}_online.htm`;
}

export const DataCell = column.connectDataCell(({ className, value }) => (
  <td className={className}>
    <a
      target="_blank"
      rel="noopener noreferrer"
      href={createGsaAdvantageUrl(value)}
    >
      {value} {DOCUMENT_SVG}
    </a>
  </td>
));
