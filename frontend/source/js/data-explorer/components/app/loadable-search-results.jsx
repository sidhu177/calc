import LoadableWrapper from '../loadable-wrapper';

const LoadableSearchResults = LoadableWrapper(
  () => import('./search-results'));

export default LoadableSearchResults;
