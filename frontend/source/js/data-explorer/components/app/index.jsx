import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import classNames from 'classnames';

import {
  resetState,
  invalidateRates,
} from '../../actions';


import QueryType from '../query-type';
import LaborCategory from '../labor-category';
import TitleTagSynchronizer from '../title-tag-synchronizer';
import LoadingIndicator from '../loading-indicator';

import LoadableSearchResults from './loadable-search-results';

import { autobind } from '../../util';


/**
 * TODO:
 *   - add a no results component/alert to search-results.jsx
 *   - Think about/improve the hasRates prop
 *   - Probably extract the #search section to its own component
 *   - Think about/improve where redux state is connected
 */


class App extends React.Component {
  constructor(props) {
    super(props);
    autobind(this, [
      'handleSubmit',
      'handleResetClick',
    ]);
  }

  getContainerClassNames() {
    let loaded = false;
    let loading = false;
    let error = false;

    if (this.props.ratesInProgress) {
      loading = true;
    } else if (this.props.ratesError) {
      if (this.props.ratesError !== 'abort') {
        error = true;
        loaded = true;
      }
    } else {
      loaded = true;
    }

    return {
      search: true,
      content: true,
      loaded,
      loading,
      error,
    };
  }

  handleSubmit(e) {
    e.preventDefault();
    this.props.invalidateRates();
  }

  handleResetClick(e) {
    e.preventDefault();
    this.props.resetState();
  }

  render() {
    const prefixId = name => `${this.props.idPrefix}${name}`;
    const { hasRates, ratesInProgress, ratesReturned } = this.props;

    return (
      <form
        id={prefixId('search')}
        className={classNames(this.getContainerClassNames())}
        onSubmit={this.handleSubmit}
        role="form"
      >
        <TitleTagSynchronizer />
        <section className="search">
          <div className="container">
            <p className="help-text">
              Enter your search terms below, separated by commas.
              {' '}
              (For example: Engineer, Consultant)
            </p>
            <div className="row">
              <div className="twelve columns">
                <LaborCategory api={this.props.api}>
                  <button className="submit usa-button-primary">
                    Search
                  </button>
                  {' '}
                  {hasRates && <input
                    onClick={this.handleResetClick}
                    className="reset usa-button usa-button-outline"
                    type="reset"
                    value="Clear search"
                  />}
                </LaborCategory>
              </div>
              <div className="twelve columns">
                <div id={prefixId('query-types')}>
                  <QueryType />
                </div>
              </div>
            </div>
          </div>
        </section>

        <LoadingIndicator />

        {((!ratesInProgress && hasRates) || !ratesReturned) &&
          <LoadableSearchResults {...this.props} />
        }
      </form>
    );
  }
}

App.propTypes = {
  api: PropTypes.object.isRequired,
  ratesInProgress: PropTypes.bool.isRequired,
  ratesError: PropTypes.string,
  resetState: PropTypes.func.isRequired,
  invalidateRates: PropTypes.func.isRequired,
  hasRates: PropTypes.bool,
  idPrefix: PropTypes.string,
};

App.defaultProps = {
  idPrefix: '',
  ratesError: null,
  hasRates: false,
  ratesReturned: null,
};

export default connect(
  state => ({
    ratesInProgress: state.rates.inProgress,
    ratesError: state.rates.error,
    hasRates: !!(state.rates.data && state.rates.data.results.length && state.q),
    ratesReturned: state.rates.data.results,
  }),
  { resetState, invalidateRates },
)(App);
