
import React, { useEffect, useMemo, useRef, useState } from 'react';
import axios from 'axios';
import {
  Alert,
  AppBar,
  Box,
  Button,
  Chip,
  CircularProgress,
  Container,
  CssBaseline,
  Divider,
  Grid,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Toolbar,
  Typography,
  Link,
  Tabs,
  Tab,
  Tooltip
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import SkipToContent from './components/SkipToContent';
import OnboardingBanner from './components/OnboardingBanner';
import HelpFab from './components/HelpFab';
import './App.css';



const DEFAULT_INTENT = 'Onboard a new customer and send a welcome email to the account owner.';
const ALLOWED_DOMAINS = ['opsai.com', 'enterprise.corp', 'gmail.com'];
const STAGE_ORDER = ['INTERPRETING', 'PLANNING', 'EXECUTING', 'GOVERNANCE'];

const generateUuid = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  const template = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx';
  return template.replace(/[xy]/g, (char) => {
    const rand = (Math.random() * 16) | 0;
    const value = char === 'x' ? rand : ((rand & 0x3) | 0x8);
    return value.toString(16);
  });
};

const formatJson = (value) => {
  if (!value) return '-';
  if (typeof value === 'string') return value;
  try {
    return JSON.stringify(value, null, 2);
  } catch (error) {
    return String(value);
  }
};

/**
 * App - Main application component for OpsAI UI.
 * Handles orchestration workspace, onboarding, help, and dark mode.
 * @returns {JSX.Element}
 */
function App() {
  const [showHelp, setShowHelp] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  // Toggle dark mode class on body
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
  }, [darkMode]);

  const theme = useMemo(() => createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: { main: darkMode ? '#60a5fa' : '#1f3a8a' },
      secondary: { main: darkMode ? '#34d399' : '#0f766e' },
      background: {
        default: darkMode ? '#181a20' : '#f5f6fa',
        paper: darkMode ? '#23262f' : '#fff'
      },
      error: { main: '#ef4444' },
      warning: { main: '#f59e42' },
      info: { main: '#3b82f6' },
      success: { main: '#22c55e' },
      divider: darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)'
    },
    typography: {
      fontFamily: '"Inter", "Segoe UI", "Helvetica Neue", Arial, sans-serif',
      h6: { fontWeight: 600 },
      subtitle1: { fontWeight: 600 }
    },
    components: {
      MuiPaper: {
        styleOverrides: {
          root: {
            border: `1px solid ${darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15, 23, 42, 0.08)'}`,
            boxShadow: darkMode
              ? '0 2px 16px 0 rgba(0,0,0,0.25)'
              : '0 2px 16px 0 rgba(31,58,138,0.06)',
            transition: 'box-shadow 0.2s, border 0.2s, background 0.2s',
            background: darkMode ? '#23262f' : '#fff'
          }
        }
      },
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            fontWeight: 600,
            borderRadius: 10,
            transition: 'background 0.2s, color 0.2s, box-shadow 0.2s',
            boxShadow: 'none',
            '&:hover': {
              boxShadow: darkMode
                ? '0 4px 20px 0 rgba(96,165,250,0.10)'
                : '0 4px 20px 0 rgba(31,58,138,0.10)'
            }
          }
        }
      },
      MuiChip: {
        styleOverrides: {
          root: {
            fontWeight: 600,
            borderRadius: 8,
            letterSpacing: 0.1,
            transition: 'background 0.2s, color 0.2s',
          }
        }
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            background: darkMode
              ? 'linear-gradient(90deg, #23262f 0%, #1f2937 100%)'
              : 'linear-gradient(90deg, #1f3a8a 0%, #60a5fa 100%)',
            color: darkMode ? '#fff' : '#fff',
            boxShadow: 'none',
            borderBottom: `1px solid ${darkMode ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.12)'}`,
            transition: 'background 0.2s, border 0.2s'
          }
        }
      }
    },
    shape: {
      borderRadius: 14
    },
    transitions: {
      duration: {
        shortest: 120,
        shorter: 180,
        short: 250,
        standard: 300,
        complex: 375,
        enteringScreen: 225,
        leavingScreen: 195
      }
    }
  }), [darkMode]);
  const [inputText, setInputText] = useState(DEFAULT_INTENT);
  const [organizationId, setOrganizationId] = useState(generateUuid);
  const [userId, setUserId] = useState(generateUuid);
  const [orchestrationId, setOrchestrationId] = useState('');
  const [status, setStatus] = useState('IDLE');
  const [events, setEvents] = useState([]);
  const [streamState, setStreamState] = useState('idle');
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState('');

  const streamRef = useRef(null);

  const canApprove = status === 'PENDING_APPROVAL';
  const canReject = status === 'PENDING_APPROVAL';
  const [showFullLog, setShowFullLog] = useState(false);
  const [mainTab, setMainTab] = useState(0);
  const [streamEnabled, setStreamEnabled] = useState(true);

  const statusTone = (value) => {
    switch (value) {
      case 'PENDING_APPROVAL':
        return 'warning';
      case 'EXECUTING':
      case 'PLANNING':
      case 'INTERPRETING':
        return 'info';
      case 'COMPLETED':
        return 'success';
      case 'FAILED':
      case 'REJECTED':
        return 'error';
      default:
        return 'default';
    }
  };

  const streamTone = (value) => {
    if (value === 'open') return 'success';
    if (value === 'error') return 'error';
    if (value === 'connecting') return 'warning';
    return 'default';
  };

  const latestByStage = useMemo(() => {
    const stages = new Map();
    events.forEach((event) => {
      const stage = event.stage || 'EVENT';
      stages.set(stage, event);
    });
    return Array.from(stages.values());
  }, [events]);

  const stageTimeline = useMemo(() => (
    STAGE_ORDER.map((stage) => {
      const match = [...events].reverse().find((event) => event.stage === stage);
      return {
        stage,
        status: match?.status || 'PENDING',
        timestamp: match?.received_at || null
      };
    })
  ), [events]);

  const validationIssues = useMemo(() => {
    if (!detail?.workflow?.steps) return [];
    const issues = [];
    detail.workflow.steps.forEach((step) => {
      if (step.type === 'COMMUNICATION') {
        const toValue = step.payload?.to;
        if (!toValue) {
          issues.push(`Step "${step.step_id}" is missing a recipient email.`);
        }
      }
    });
    return issues;
  }, [detail]);

  const lastFailure = useMemo(() => {
    if (!detail?.steps) return null;
    const failed = [...detail.steps].reverse().find((step) => step.status === 'FAILED');
    if (!failed) return null;
    return failed.error || failed.result || 'Unknown failure';
  }, [detail]);

  const latestEvent = useMemo(() => events[events.length - 1], [events]);

  const orchestrationLabel = useMemo(() => (
    orchestrationId ? `${orchestrationId.slice(0, 8)}...` : 'Not started'
  ), [orchestrationId]);

  const fetchDetail = React.useCallback(async (id = orchestrationId) => {
    if (!id) return;
    setDetailLoading(true);
    try {
      const response = await axios.get(`/api/orchestrations/${id}`);
      setDetail(response.data);
    } catch (err) {
      setError(err?.response?.data?.error?.message || err.message);
    } finally {
      setDetailLoading(false);
    }
  }, [orchestrationId]);

  const handleStart = async () => {
    setLoading(true);
    setError('');
    setDetail(null);
    setEvents([]);
    setStatus('PENDING');
    setStreamEnabled(true);
    try {
      const response = await axios.post('/api/orchestrate', {
        input_text: inputText,
        organization_id: organizationId,
        user_id: userId
      });
      setOrchestrationId(response.data.id);
      setStatus(response.data.status || 'PENDING');
    } catch (err) {
      setError(err?.response?.data?.error?.message || err.message);
      setStatus('FAILED');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!orchestrationId) return;
    setLoading(true);
    setError('');
    try {
      await axios.post(`/api/orchestrate/${orchestrationId}/approve`);
      setStatus('EXECUTING');
      await fetchDetail();
    } catch (err) {
      setError(err?.response?.data?.error?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    if (!orchestrationId) return;
    setLoading(true);
    setError('');
    try {
      await axios.post(`/api/orchestrate/${orchestrationId}/reject`);
      setStatus('REJECTED');
      await fetchDetail();
    } catch (err) {
      setError(err?.response?.data?.error?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    if (streamRef.current) {
      streamRef.current.close();
      streamRef.current = null;
    }
    setInputText(DEFAULT_INTENT);
    setOrganizationId(generateUuid());
    setUserId(generateUuid());
    setOrchestrationId('');
    setStatus('IDLE');
    setEvents([]);
    setStreamState('idle');
    setStreamEnabled(false);
    setDetail(null);
    setError('');
  };

  const handleStopStream = () => {
    if (streamRef.current) {
      streamRef.current.close();
      streamRef.current = null;
    }
    setStreamState('idle');
    setStreamEnabled(false);
  };

  const handleResumeStream = () => {
    if (!orchestrationId) return;
    setStreamEnabled(true);
  };

  useEffect(() => {
    if (!orchestrationId || !streamEnabled) return;
    if (streamRef.current) {
      streamRef.current.close();
    }
    const source = new EventSource(`/api/orchestrate/${orchestrationId}/stream`);
    streamRef.current = source;
    setStreamState('connecting');

    source.onopen = () => setStreamState('open');
    source.onerror = () => setStreamState('error');
    source.onmessage = (event) => {
      if (!event?.data) return;
      let payload = null;
      try {
        payload = JSON.parse(event.data);
      } catch (err) {
        payload = { raw: event.data };
      }
      setEvents((prev) => [
        ...prev,
        { ...payload, received_at: new Date().toISOString() }
      ]);
      if (payload?.status) {
        setStatus(payload.status);
      }
      if (payload?.stage === 'GOVERNANCE' && payload?.status === 'PENDING_APPROVAL') {
        fetchDetail();
      }
    };

    return () => {
      source.close();
    };
  }, [orchestrationId, fetchDetail, streamEnabled]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SkipToContent />
      <OnboardingBanner />
      <Box className="app-shell">
        <AppBar position="static" color="primary" elevation={0}>
          <Toolbar sx={{ minHeight: 68 }}>
            <Box>
              <Typography variant="h6">OpsAI Control Plane</Typography>
              <Typography variant="caption" sx={{ opacity: 0.8 }}>
                Governed orchestration for enterprise operations
              </Typography>
            </Box>
            <Box sx={{ flexGrow: 1 }} />
            <Stack direction="row" spacing={1} alignItems="center">
              <Chip label={`Stream: ${streamState}`} color={streamTone(streamState)} sx={{ display: { xs: 'none', md: 'inline-flex' } }} />
              <Chip label="Demo" sx={{ display: { xs: 'none', md: 'inline-flex' } }} />
              <Button color="inherit" size="small" variant="text">Docs</Button>
              <Button color="inherit" size="small" variant="text">Status</Button>
              {/* Removed Sign out button as it has no functionality */}
              <Button
                color="secondary"
                size="small"
                variant={darkMode ? 'contained' : 'outlined'}
                sx={{ ml: 1, minWidth: 40 }}
                onClick={() => setDarkMode((prev) => !prev)}
                aria-label="Toggle dark mode"
              >
                {darkMode ? '🌙' : '☀️'}
              </Button>
            </Stack>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ py: 3 }} id="main-content" tabIndex={-1}>
                <HelpFab onClick={() => setShowHelp(true)} />
                {showHelp && (
                  <Box className="help-modal" role="dialog" aria-modal="true" tabIndex={-1}>
                    <Paper sx={{ p: 3, maxWidth: 400, mx: 'auto', my: 8 }}>
                      <Typography variant="h6">OpsAI Quick Help</Typography>
                      <ul>
                        <li>Describe your intent and click <b>Start Orchestration</b>.</li>
                        <li>Approve or reject plans at the Governance Gate.</li>
                        <li>Use the <b>Dark Mode</b> toggle for your preference.</li>
                        <li>Keyboard: <b>Tab</b> to navigate, <b>Enter</b> to activate, <b>Esc</b> to close help.</li>
                      </ul>
                      <Button onClick={() => setShowHelp(false)} variant="outlined" aria-label="Close help">Close</Button>
                    </Paper>
                  </Box>
                )}
          <Grid container spacing={3}>
            <Grid item xs={12} lg={3}>
              <Paper elevation={0} className="sidebar-card">
                <Stack spacing={2}>
                  <Typography variant="overline">Navigation</Typography>
                  <Stack spacing={1}>
                    <Button variant="contained" size="small" className="nav-button">Overview</Button>
                    <Button variant="text" size="small" className="nav-button">Orchestrations</Button>
                    <Button variant="text" size="small" className="nav-button">Governance</Button>
                    <Button variant="text" size="small" className="nav-button">Activity</Button>
                    <Button variant="text" size="small" className="nav-button">Settings</Button>
                  </Stack>
                  <Divider />
                  <Typography variant="overline">Session</Typography>
                  <Stack spacing={1}>
                    <Typography variant="body2">{orchestrationLabel}</Typography>
                    <Chip label={`Status: ${status}`} color={statusTone(status)} />
                    <Typography variant="caption" color="text.secondary">
                      Latest event: {latestEvent?.stage || 'Idle'}
                    </Typography>
                  </Stack>
                </Stack>
              </Paper>
            </Grid>

            <Grid item xs={12} lg={9}>
              <Stack spacing={3}>
                <Paper elevation={0} className="hero-card">
                  <Stack spacing={1}>
                    <Typography variant="h5">Orchestration Workspace</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Plan, review, and approve automated workflows with traceable governance.
                    </Typography>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
                      <Chip label={`Orchestration: ${orchestrationLabel}`} />
                      <Chip label={`Status: ${status}`} color={statusTone(status)} />
                      <Chip label={`Latest: ${latestEvent?.stage || 'Idle'}`} />
                    </Stack>
                  </Stack>
                </Paper>

                <Paper elevation={0} className="summary-card">
                  <Grid container spacing={0}>
                    <Grid item xs={12} md={4}>
                      <Box className="summary-item">
                        <Typography variant="overline">Orchestration</Typography>
                        <Typography variant="h6">{orchestrationLabel}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          Current session identifier
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Box className="summary-item">
                        <Typography variant="overline">Status</Typography>
                        <Stack direction="row" spacing={1} alignItems="center">
                          <Chip label={status} color={statusTone(status)} />
                          <Typography variant="body2" color="text.secondary">
                            {status === 'PENDING_APPROVAL' ? 'Awaiting approval' : 'Pipeline state'}
                          </Typography>
                        </Stack>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Box className="summary-item summary-item-last">
                        <Typography variant="overline">Latest Event</Typography>
                        <Typography variant="h6">{latestEvent?.stage || 'Idle'}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {latestEvent?.received_at || 'No events yet'}
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </Paper>

                {error && <Alert severity="error">{error}</Alert>}

                <Tabs value={mainTab} onChange={(_, v) => setMainTab(v)} sx={{ mb: 2 }}>
                  <Tab label="Pipeline Timeline" />
                  <Tab label="Live Reasoning Stream" />
                  <Tab label="Workflow & Step History" />
                </Tabs>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    {mainTab === 0 && (
                      <Paper elevation={0} className="section-card section-card--tall">
                  <Stack spacing={2}>
                    <Box className="section-header">
                      <Typography variant="subtitle1">New Orchestration</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Provide the intent and identifiers to generate a governed plan.
                      </Typography>
                    </Box>
                    <TextField
                      label="Intent"
                      multiline
                      minRows={4}
                      value={inputText}
                      onChange={(event) => setInputText(event.target.value)}
                      placeholder="Describe what you want OpsAI to orchestrate"
                      fullWidth
                    />
                    <Stack spacing={2}>
                      <TextField
                        label="Organization ID"
                        value={organizationId}
                        onChange={(event) => setOrganizationId(event.target.value)}
                        helperText="UUID for demo data"
                        fullWidth
                        size="small"
                      />
                      <TextField
                        label="User ID"
                        value={userId}
                        onChange={(event) => setUserId(event.target.value)}
                        helperText="UUID for demo data"
                        fullWidth
                        size="small"
                      />
                    </Stack>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center" sx={{ mt: 1 }}>
                      <Button
                        variant="contained"
                        color="primary"
                        size="large"
                        startIcon={!loading && <PlayArrowIcon />}
                        onClick={handleStart}
                        disabled={loading || !inputText.trim()}
                        fullWidth
                        sx={{ fontWeight: 700, fontSize: '1.1rem', py: 1.5 }}
                        aria-label="Start Orchestration"
                      >
                        {loading ? <CircularProgress size={20} /> : 'Start Orchestration'}
                      </Button>
                      <Button variant="outlined" onClick={handleReset} disabled={loading} fullWidth sx={{ py: 1.5 }}>
                        Reset
                      </Button>
                    </Stack>
                  </Stack>
                </Paper>

                <Paper elevation={0} className="section-card section-card--medium">
                  <Stack spacing={2}>
                    <Box className="section-header">
                      <Tooltip title="The Governance Gate is where you approve or reject plans before execution." arrow>
                        <Typography variant="h6" sx={{ display: 'inline-flex', alignItems: 'center' }}>Governance Gate</Typography>
                      </Tooltip>
                      <Typography variant="body2" color="text.secondary">
                        Approve or reject once the plan reaches the PENDING_APPROVAL stage.
                      </Typography>
                    </Box>
                    {validationIssues.length > 0 && (
                      <Alert severity="warning">
                        Approval blocked:
                        <ul>
                          {validationIssues.map((issue) => (
                            <li key={issue}>{issue}</li>
                          ))}
                        </ul>
                      </Alert>
                    )}
                    {lastFailure && (
                      <Alert severity="error">
                        Latest execution failure: {formatJson(lastFailure)}
                      </Alert>
                    )}
                    <Divider />
                    <Typography variant="subtitle2">Security policy</Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      {ALLOWED_DOMAINS.map((domain) => (
                        <Chip key={domain} size="small" label={domain} />
                      ))}
                    </Stack>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                      <Button
                        variant="contained"
                        onClick={handleApprove}
                        disabled={!canApprove || loading || validationIssues.length > 0}
                      >
                        Approve & Execute
                      </Button>
                      <Button variant="outlined" color="error" onClick={handleReject} disabled={!canReject || loading}>
                        Reject
                      </Button>
                      <Button variant="text" onClick={() => fetchDetail()} disabled={!orchestrationId || detailLoading}>
                        {detailLoading ? <CircularProgress size={18} /> : 'Refresh Details'}
                      </Button>
                    </Stack>
                  </Stack>
                </Paper>

                    )}
                    {mainTab === 1 && (
                      <Paper elevation={0} className="section-card section-card--medium">
                        <Stack spacing={2}>
                          <Box display="flex" alignItems="center" justifyContent="space-between">
                            <Typography variant="h6">Live Reasoning Stream</Typography>
                            <Button size="small" variant="outlined" onClick={() => setShowFullLog((prev) => !prev)}>
                              {showFullLog ? 'Hide Stream' : 'Show Stream'}
                            </Button>
                          </Box>
                          <Divider />
                          {showFullLog && (
                            events.length === 0 ? (
                              <Typography variant="body2" color="text.secondary" sx={{ my: 2 }}>
                                Start an orchestration to see stage updates here.<br />
                                <Link href="/docs/getting-started" target="_blank" rel="noopener">Learn how to run your first orchestration.</Link>
                              </Typography>
                            ) : (
                              <Stack spacing={2}>
                                <Stack spacing={1}>
                                  {latestByStage.map((item, index) => (
                                    <Paper key={`${item.stage || 'event'}-${index}`} variant="outlined" className="event-card">
                                      <Stack spacing={0.5} sx={{ p: 1.5 }}>
                                        <Stack direction="row" spacing={1} alignItems="center">
                                          <Chip size="small" label={item.stage || 'EVENT'} />
                                          <Chip size="small" label={item.status || 'UNKNOWN'} color={statusTone(item.status)} />
                                          <Typography variant="caption" color="text.secondary">
                                            {item.received_at}
                                          </Typography>
                                        </Stack>
                                        <pre className="event-payload">{formatJson(item)}</pre>
                                      </Stack>
                                    </Paper>
                                  ))}
                                </Stack>
                                <Button variant="text" onClick={() => setShowFullLog((prev) => !prev)}>
                                  {showFullLog ? 'Hide full stream' : 'Show full stream'}
                                </Button>
                                {showFullLog && (
                                  <Stack spacing={1} className="event-log">
                                    {events.map((item, index) => (
                                      <Paper key={`${item.stage || 'event'}-${index}`} variant="outlined" className="event-card">
                                        <Stack spacing={0.5} sx={{ p: 1.5 }}>
                                          <Stack direction="row" spacing={1} alignItems="center">
                                            <Chip size="small" label={item.stage || 'EVENT'} />
                                            <Chip size="small" label={item.status || 'UNKNOWN'} color={statusTone(item.status)} />
                                            <Typography variant="caption" color="text.secondary">
                                              {item.received_at}
                                            </Typography>
                                          </Stack>
                                          <pre className="event-payload">{formatJson(item)}</pre>
                                        </Stack>
                                      </Paper>
                                    ))}
                                  </Stack>
                                )}
                              </Stack>
                            )
                          )}
                        </Stack>
                      </Paper>
                    )}
                    {mainTab === 2 && (
                      <Paper elevation={0} className="section-card section-card--tall">
                        <Stack spacing={2}>
                          <Typography variant="h6">Workflow & Step History</Typography>
                          {detailLoading && !detail ? (
                            <CircularProgress />
                          ) : detail ? (
                            <>
                              <Typography variant="subtitle2">Workflow Steps</Typography>
                              <Grid container spacing={2}>
                                {detail.workflow?.steps?.map((step, idx) => (
                                  <Grid item xs={12} md={6} key={`${step.step_id}-${idx}`}>
                                    <Paper variant="outlined" className="step-card">
                                      <Stack spacing={1}>
                                        <Stack direction="row" spacing={1} alignItems="center">
                                          <Typography variant="subtitle2">{step.step_id}</Typography>
                                          <Chip size="small" label={step.type} />
                                          <Chip size="small" label={step.priority} color="info" />
                                        </Stack>
                                        <Typography variant="body2">{step.action}</Typography>
                                        <Typography variant="caption" color="text.secondary">
                                          Owner: {step.owner}
                                        </Typography>
                                        {step.payload && (
                                          <pre className="event-payload">{formatJson(step.payload)}</pre>
                                        )}
                                      </Stack>
                                    </Paper>
                                  </Grid>
                                ))}
                              </Grid>
                              <TableContainer component={Paper} variant="outlined" sx={{ overflowX: 'auto' }}>
                                <Table size="small">
                                  <TableHead>
                                    <TableRow>
                                      <TableCell>Step ID</TableCell>
                                      <TableCell>Type</TableCell>
                                      <TableCell>Action</TableCell>
                                      <TableCell>Owner</TableCell>
                                      <TableCell>Priority</TableCell>
                                    </TableRow>
                                  </TableHead>
                                  <TableBody>
                                    {detail.workflow?.steps?.map((step, idx) => (
                                      <TableRow key={`${step.step_id}-${idx}`}>
                                        <TableCell>{step.step_id}</TableCell>
                                        <TableCell>{step.type}</TableCell>
                                        <TableCell>{step.action}</TableCell>
                                        <TableCell>{step.owner}</TableCell>
                                        <TableCell>{step.priority}</TableCell>
                                      </TableRow>
                                    ))}
                                  </TableBody>
                                </Table>
                              </TableContainer>
                              <Typography variant="subtitle2">Step History</Typography>
                              <TableContainer component={Paper} variant="outlined" sx={{ overflowX: 'auto' }}>
                                <Table size="small">
                                  <TableHead>
                                    <TableRow>
                                      <TableCell>Step ID</TableCell>
                                      <TableCell>Status</TableCell>
                                      <TableCell>Result / Error</TableCell>
                                    </TableRow>
                                  </TableHead>
                                  <TableBody>
                                    {detail.steps?.map((step, idx) => (
                                      <TableRow key={`${step.step_id}-${idx}`}>
                                        <TableCell>{step.step_id}</TableCell>
                                        <TableCell>{step.status}</TableCell>
                                        <TableCell>{formatJson(step.result || step.error || '-')}</TableCell>
                                      </TableRow>
                                    ))}
                                  </TableBody>
                                </Table>
                              </TableContainer>
                            </>
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              No workflow details yet. Run an orchestration and refresh after planning.
                            </Typography>
                          )}
                        </Stack>
                      </Paper>
                    )}
                                <TableRow key={`${step.step_id}-${idx}`}>
                                  <TableCell>{step.step_id}</TableCell>
                                  <TableCell>{step.status}</TableCell>
                                  <TableCell>{formatJson(step.result || step.error || '-')}</TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No workflow details yet. Run an orchestration and refresh after planning.
                      </Typography>
                    )}
                  </Stack>
                </Paper>
              </Grid>
            </Grid>
            </Stack>
          </Grid>
        </Grid>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
