/**
 * SkipToContent - Accessibility link to jump to main content.
 * @returns {JSX.Element}
 */
import React from 'react';

const SkipToContent = () => (
  <a
    href="#main-content"
    className="skip-to-content"
    tabIndex={0}
    aria-label="Skip to main content"
  >
    Skip to main content
  </a>
);

export default SkipToContent;
