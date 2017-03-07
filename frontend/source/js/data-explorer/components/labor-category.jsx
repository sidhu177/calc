import React from 'react';
import { connect } from 'react-redux';
import Autosuggest from 'react-autosuggest';

import { setQuery } from '../actions';

import { MAX_QUERY_LENGTH, MAX_AUTOCOMPLETE_RESULTS } from '../constants';

import {
  autobind,
  handleEnter,
  filterActive,
  getLastCommaSeparatedTerm,
} from '../util';

// TODO: handle enter and select


// TODO: min number of characters before request?
// TODO: debouncing?
// TODO: Maybe with a middleware: http://stackoverflow.com/questions/40088673/debounce-api-call-in-redux

export class LaborCategory extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      value: this.props.query,
      suggestions: [],
      isLoading: false,
    };
    autobind(this, ['handleChange', 'handleEnter', 'loadSuggestions',
      'onSuggestionsClearRequested', 'onSuggestionSelected']);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.query !== this.props.query) {
      this.setState({ value: nextProps.query });
    }
  }

  onSuggestionsClearRequested() {
    // TODO: this.request.abort() ?
    this.setState({ suggestions: [] });
  }

  onSuggestionSelected(e, { suggestion }) {
    console.log(suggestion);
  }

  handleChange(e, { newValue }) {
    // const searchTerms = this.state.value;
    // let selectedInput;
    //
    // if (searchTerms.indexOf(',') !== -1) {
    //   const termSplit = searchTerms.split(', ');
    //   // remove last typed (incomplete) input
    //   termSplit.pop();
    //   // combine existing search terms with new one
    //   selectedInput = `${termSplit.join(', ')}, ${newValue}, `;
    // // if search field doesn't have terms
    // // but has selected an autocomplete suggestion,
    // // then just show term and comma delimiter
    // } else {
    //   selectedInput = `${newValue}, `;
    // }

    this.setState({ value: newValue });
  }

  handleEnter() {
    if (this.state.value !== this.props.query) {
      this.props.setQuery(this.state.value);
    }
  }

  loadSuggestions({ value }) {
    const lastTerm = getLastCommaSeparatedTerm(value);

    if (this.request) {
      this.request.abort();
      this.request = null;
    }

    this.setState({ isLoading: true });

    this.request = this.props.api.get({
      uri: 'search/',
      data: {
        q: lastTerm,
        query_type: this.props.queryType,
      },
    }, (error, result) => {
      this.request = null;
      if (error) {
        this.setState({ suggestions: [], isLoading: false });
        return;
      }
      const suggestions = result.slice(0, MAX_AUTOCOMPLETE_RESULTS)
                                .map(r => r.labor_category);
      this.setState({ suggestions, isLoading: false });
    });
  }

  render() {
    const id = `${this.props.idPrefix}labor_category`;
    const className = filterActive(this.props.query !== '', 'form__inline');

    const inputProps = {
      id,
      className,
      name: 'q',
      type: 'text',
      placeholder: 'Type a labor category',
      value: this.state.value,
      onChange: this.handleChange,
      onKeyDown: handleEnter(this.handleEnter),
      maxLength: MAX_QUERY_LENGTH,
    };

    return (
      <div>
        <Autosuggest
          suggestions={this.state.suggestions}
          onSuggestionsFetchRequested={this.loadSuggestions}
          onSuggestionsClearRequested={this.onSuggestionsClearRequested}
          onSuggestionSelected={this.onSuggestionSelected}
          getSuggestionValue={v => v}
          renderSuggestion={v => v}
          shouldRenderSuggestions={v => v.trim().length > 2}
          inputProps={inputProps}
        />
        <label htmlFor={id} className="sr-only">Type a labor category</label>
        {this.props.children}
      </div>
    );

    // return (
    //   <div>
    //     <input
    //       id={id} name="q" placeholder="Type a labor category"
    //       className={className} type="text"
    //       ref={(el) => { this.inputEl = el; }}
    //       value={this.state.value}
    //       onChange={this.handleChange}
    //       onKeyDown={handleEnter(this.handleEnter)}
    //       maxLength={MAX_QUERY_LENGTH}
    //     />
    //     <label htmlFor={id} className="sr-only">Type a labor category</label>
    //     {this.props.children}
    //   </div>
    // );
  }
}

LaborCategory.propTypes = {
  idPrefix: React.PropTypes.string,
  query: React.PropTypes.string.isRequired,
  queryType: React.PropTypes.string.isRequired,
  setQuery: React.PropTypes.func.isRequired,
  api: React.PropTypes.object.isRequired,
  children: React.PropTypes.any,
};

LaborCategory.defaultProps = {
  idPrefix: '',
  children: null,
};

export default connect(
  state => ({
    query: state.q,
    queryType: state.query_type,
  }),
  { setQuery },
)(LaborCategory);
