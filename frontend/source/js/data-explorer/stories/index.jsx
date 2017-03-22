import React from 'react';
import { storiesOf, action } from '@kadira/storybook';

import * as constants from '../constants';
import { EducationLevel } from '../components/education-level';
import Tooltip from '../components/tooltip';

storiesOf('EducationLevel', module)
  .add('with none selected', () => (
    <EducationLevel
      levels={[]}
      toggleEducationLevel={action('toggled')}
    />
  ))
  .add('with one selected', () => (
    <EducationLevel
      levels={[constants.EDU_HIGH_SCHOOL]}
      toggleEducationLevel={action('toggled')}
    />
  ));

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
          I am a keyboard-focusable tooltip.
        </a>
      </Tooltip>
    ),
  )
  .add('always showing', () => (
    <Tooltip text="I am always showing!" show>
      This text will have a permanently visible tooltip.
    </Tooltip>
  ));
