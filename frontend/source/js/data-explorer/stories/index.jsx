import React from 'react';
import { storiesOf } from '@kadira/storybook';
import { createStore } from 'redux';
import { Provider } from 'react-redux';

import appReducer from '../reducers';
import EducationLevel from '../components/education-level';
import Tooltip from '../components/tooltip';

storiesOf('EducationLevel', module)
  .add(
    'with none selected',
    () => (
      <Provider store={createStore(appReducer)}>
        <EducationLevel />
      </Provider>
    ),
  );

storiesOf('Tooltip', module)
  .addWithInfo(
    'showing on focus/hover',
    `
      The tooltip automatically shows and hides itself on focus
      and blur events, so wrapping a focusable element in a tooltip
      keeps things accessible for keyboard users.

      This is not actually very friendly to screen reader users
      because ATs will still identify the element as a link, but
      it's better than nothing.
    `,
    () => (
      <Tooltip text="Hello, I am a tooltip!">
        <a
          href=""
          aria-label="Hello, I am a tooltip!"
          onClick={(e) => { e.preventDefault(); }}
        >
          Here is a keyboard-focusable tooltip.
        </a>
      </Tooltip>
    ),
  )
  .addWithInfo(
    'always showing',
    `
      This can be useful if you need external state or code to
      control when the tooltip shows.
    `,
    () => (
      <Tooltip text="I am always showing!" show>
        This text will have a permanently visible tooltip.
      </Tooltip>
    ),
  );
