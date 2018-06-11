// @ts-check
/* global $, window, document */

import ReactDOM from 'react-dom';
import React from 'react';
import { createStore, applyMiddleware } from 'redux';
import { Provider } from 'react-redux';

import App from './components/app';

import { trackVirtualPageview } from '../common/ga';

import appReducer from './reducers';

import StoreHistorySynchronizer from './history';

import StoreRatesAutoRequester from './rates-request';

import API from './api';

const api = new API();
const historySynchronizer = new StoreHistorySynchronizer(window);
const ratesRequester = new StoreRatesAutoRequester(api);
const middlewares = [
  ratesRequester.middleware,
  historySynchronizer.reflectToHistoryMiddleware,
];

if (process.env.NODE_ENV !== 'production') {
  // We only want to include logging middleware code in non-production
  // JS bundles, so we're going to conditionally require it here.
  const createLogger = require('redux-logger');  // eslint-disable-line global-require

  middlewares.push(createLogger());
}

const store = createStore(
  appReducer,
  applyMiddleware(...middlewares),
);

// set default options for all future tooltip instantiations
$.fn.tooltipster('setDefaults', {
  speed: 200,
});

historySynchronizer.initialize(store, () => {
  trackVirtualPageview();
});

// Load the React app once the document is ready
$(() => {
  ReactDOM.render(
    React.createElement(
      Provider,
      { store },
      React.createElement(App, { api }),
    ),
    $('[data-embed-jsx-app-here]')[0],
  );
});
