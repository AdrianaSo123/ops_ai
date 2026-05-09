/**
 * OnboardingBanner - Dismissible onboarding banner for new users.
 * @param {Object} props
 * @param {Function} [props.onClose] - Optional callback when dismissed.
 * @returns {JSX.Element|null}
 */
import React, { useState } from 'react';
import { Box, Button } from '@mui/material';

const OnboardingBanner = ({ onClose }) => {
  const [open, setOpen] = useState(true);
  if (!open) return null;
  return (
    <Box className="onboarding-banner" role="region" aria-label="Onboarding">
      <span>
        👋 Welcome to OpsAI! Start by describing your intent and clicking "Start Orchestration". Use the help button for tips.
      </span>
      <Button
        size="small"
        variant="outlined"
        sx={{ ml: 2 }}
        onClick={() => { setOpen(false); onClose && onClose(); }}
        aria-label="Dismiss onboarding banner"
      >
        Dismiss
      </Button>
    </Box>
  );
};

export default OnboardingBanner;
