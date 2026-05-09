/**
 * HelpFab - Floating action button for help/tips.
 * @param {Object} props
 * @param {Function} props.onClick - Click handler to open help modal.
 * @returns {JSX.Element}
 */
import React from 'react';
import { Button } from '@mui/material';

const HelpFab = ({ onClick }) => (
  <Button
    className="help-fab"
    color="secondary"
    variant="contained"
    onClick={onClick}
    aria-label="Open help and tips"
    sx={{
      position: 'fixed',
      bottom: 32,
      right: 32,
      zIndex: 1200,
      borderRadius: '50%',
      minWidth: 56,
      minHeight: 56,
      boxShadow: 6,
      fontSize: 28
    }}
  >
    ?
  </Button>
);

export default HelpFab;
