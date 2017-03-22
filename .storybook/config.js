import { configure, setAddon } from '@kadira/storybook';
import infoAddon from '@kadira/react-storybook-addon-info';
import {
  setDefaults as infoAddonSetDefaults
} from '@kadira/react-storybook-addon-info';

function loadStories() {
  require('../frontend/source/js/data-explorer/stories/index.jsx');
}

infoAddonSetDefaults({
  inline: true,
});

setAddon(infoAddon);

configure(loadStories, module);
