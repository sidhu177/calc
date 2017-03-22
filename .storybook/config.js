import { configure } from '@kadira/storybook';

function loadStories() {
  require('../frontend/source/js/data-explorer/stories/index.jsx');
}

configure(loadStories, module);
