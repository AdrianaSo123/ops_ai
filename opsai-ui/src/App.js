
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Container,
  Typography,
  Box,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';

function OrchestrationDetail({ open, onClose, orchestration }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && orchestration) {
      setLoading(true);
      axios.get(`/api/orchestrations/${orchestration.id}`)
        .then(res => setDetail(res.data))
        .finally(() => setLoading(false));
    }
  }, [open, orchestration]);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Orchestration Details</DialogTitle>
      <DialogContent>
        {loading || !detail ? <CircularProgress /> : (
          <>
            <Typography variant="h6">Status: {detail.orchestration.status}</Typography>
            <Typography variant="subtitle1">Input: {detail.orchestration.raw_input}</Typography>
            <Box mt={2}>
              <Typography variant="subtitle2">Workflow Steps</Typography>
              <TableContainer component={Paper}>
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
                      <TableRow key={idx}>
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
            </Box>
            <Box mt={2}>
              <Typography variant="subtitle2">Step History</Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Step ID</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Result/Error</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {detail.steps?.map((step, idx) => (
                      <TableRow key={idx}>
                        <TableCell>{step.step_id}</TableCell>
                        <TableCell>{step.status}</TableCell>
                        <TableCell>{step.result || step.error || '-'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
}

function App() {
  const [orchestrations, setOrchestrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    axios.get('/api/orchestrations')
      .then(res => setOrchestrations(res.data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>OpsAI Orchestrations</Typography>
        {loading ? <CircularProgress /> : (
          <List>
            {orchestrations.map((orch) => (
              <React.Fragment key={orch.id}>
                <ListItem button onClick={() => setSelected(orch)}>
                  <ListItemText
                    primary={orch.raw_input}
                    secondary={`Status: ${orch.status} | Created: ${orch.created_at}`}
                  />
                </ListItem>
                <Divider />
              </React.Fragment>
            ))}
          </List>
        )}
      </Paper>
      <OrchestrationDetail
        open={!!selected}
        orchestration={selected}
        onClose={() => setSelected(null)}
      />
    </Container>
  );
}

export default App;
