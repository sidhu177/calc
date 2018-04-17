import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import {
  invalidateRates,
} from '../../actions';

import histogramToImg from '../../histogram-to-img';

import ga from '../../../common/ga';
import Description from '../description';
import Highlights from '../highlights';
import Histogram from '../histogram';
import ProposedPrice from '../proposed-price';
import ExportData from '../export-data';
import ResultsTable from '../results-table';
import LoadableOptionalFilters from '../optional-filters/loadable-optional-filters';

import { autobind } from '../../util';

class SearchResults extends React.Component {
  constructor(props) {
    super(props);
    autobind(this, [
      'handleDownloadClick',
    ]);
  }

  handleDownloadClick(e) {
    e.preventDefault();
    histogramToImg(
      this.histogram.getWrappedInstance().svgEl,
      this.canvasEl,
    );
    ga('send', 'event', 'download-graph', 'click');
  }

  render() {
    const prefixId = name => `${this.props.idPrefix}${name}`;
    const { ratesReturned, ratesInProgress } = this.props;

    return (
      <section className="results">
      {!ratesReturned &&
        <div className="container">
          <div className="row">
            <p>No results found!</p>
          </div>
        </div>
      }
      {ratesReturned &&
        <div className="container">
          <div className="row">

            <div className="graph-block columns nine">
              {/* for converting the histogram into an img */}
              <canvas
                ref={(el) => { this.canvasEl = el; }}
                id={prefixId('graph') /* Selenium needs it. */}
                className="hidden" width="710" height="280"
              />

              <div id={prefixId('description')}>
                <Description />
              </div>

              <h4>Hourly rate data</h4>

              <ProposedPrice />

              <div className="graph">
                <div id={prefixId('price-histogram')}>
                  <Histogram ref={(el) => { this.histogram = el; }} />
                </div>
              </div>

              <Highlights />

              <div className="download-buttons row">
                <div className="four columns">
                  <a
                    className="usa-button usa-button-primary"
                    id={prefixId('download-histogram') /* Selenium needs it. */}
                    href=""
                    onClick={this.handleDownloadClick}
                  >
                    ⬇ Download graph
                  </a>
                </div>

                <div>
                  <ExportData />
                </div>

                <p className="help-text">
                  The rates shown here are fully burdened, applicable
                  {' '}
                  worldwide, and representative of the current fiscal
                  {' '}
                  year. This data represents rates awarded at the master
                  {' '}
                  contract level.
                </p>
              </div>
            </div>

            <div className="filter-container columns three">
              <div className="filter-block">
                <h5 className="filter-title">Optional filters</h5>
                <LoadableOptionalFilters />
              </div>
            </div>

          </div>
          <div className="row">
            <div className="table-container">
              <ResultsTable />
            </div>
          </div>
        </div>
      }
      </section>
    );
  }
}

SearchResults.propTypes = {
  idPrefix: PropTypes.string,
};

SearchResults.defaultProps = {
  idPrefix: '',
  ratesError: null,
};

export default connect(
  state => ({
    ratesInProgress: state.rates.inProgress,
    ratesError: state.rates.error,
    ratesReturned: state.rates.data.results,
  }),
  { invalidateRates },
)(SearchResults);
