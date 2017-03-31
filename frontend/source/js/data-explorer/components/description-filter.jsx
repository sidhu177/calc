import React from "react";

export default function DescriptionFilter(
  {
    extraClassName,
    label,
    children
  }
) {
  let className = "filter";

  if (extraClassName) {
    className += ` ${extraClassName}`;
  }

  return (
    <span className={className}>
      {label ? `${label}: ` : null}
      <b>
        {children}
      </b>
    </span>
  );
}

DescriptionFilter.propTypes = {
  extraClassName: React.PropTypes.string,
  label: React.PropTypes.string,
  children: React.PropTypes.any.isRequired
};

DescriptionFilter.defaultProps = {
  extraClassName: null,
  label: null
};
