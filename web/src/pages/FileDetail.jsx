import Layout from "../components/Layout";
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import {
  executeWorkflow,
  getJobs,
  cancelJob,
  deleteJob,
  deleteFile,
} from "../api/api";

import {
  Button,
  Typography,
  Card,
  CardContent,
  Stack,
  Chip,
  CircularProgress,
  Paper,
  Snackbar,
  Alert,
  Grid,
} from "@mui/material";

export default function FileDetail() {
  const { fileId } = useParams();

  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [alertMessage, setAlertMessage] = useState("");
  const [alertSeverity, setAlertSeverity] = useState("success");
  const [snackbarOpen, setSnackbarOpen] = useState(false);

  useEffect(() => {
    loadJobs();
  }, [fileId]);

  const loadJobs = async () => {
    setLoading(true);
    const res = await getJobs();
    const filtered = res.data.jobs.filter((j) => j.file_id === fileId);
    setJobs(filtered);
    setLoading(false);
  };

  const runWorkflow = async (type) => {
    setActionLoading(true);

    try {
      const res = await executeWorkflow(fileId, type);
      setAlertSeverity("success");
      setAlertMessage(res?.data?.message || `Started ${type} workflow`);
      setSnackbarOpen(true);
      await loadJobs();
    } catch (error) {
      const message =
        error?.response?.data?.error ||
        error?.message ||
        "Unable to execute workflow";
      setAlertSeverity("error");
      setAlertMessage(message);
      setSnackbarOpen(true);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCloseSnackbar = (_, reason) => {
    if (reason === "clickaway") return;
    setSnackbarOpen(false);
  };

  const cancelJobHandler = async (jobId) => {
    await cancelJob(jobId);
    loadJobs();
  };

  const deleteJobHandler = async (jobId) => {
    await deleteJob(jobId);
    loadJobs();
  };

  const deleteFileHandler = async () => {
    await deleteFile(fileId);
    window.location.href = "/";
  };

  return (
    <Layout>
      <Paper
        sx={{
          p: 4,
          mb: 4,
          borderRadius: 3,
          boxShadow: "0 18px 55px rgba(15, 23, 42, 0.08)",
          backgroundColor: "#fff",
        }}
      >
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          sx={{ mb: 2 }}
        >
          <div>
            <Typography variant="h5" gutterBottom>
              File details
            </Typography>
            <Typography color="text.secondary">
              Workflows for file ID {fileId.slice(0, 8)}...
            </Typography>
          </div>

          <Button color="error" variant="outlined" onClick={deleteFileHandler}>
            Delete File
          </Button>
        </Stack>

        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              onClick={() => runWorkflow("rag")}
              disabled={actionLoading}
            >
              Run RAG
            </Button>
          </Grid>

          <Grid item xs={12} md={6}>
            <Button
              fullWidth
              variant="outlined"
              size="large"
              onClick={() => runWorkflow("summarization")}
              disabled={actionLoading}
            >
              Summarize
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {loading && (
        <Stack alignItems="center" sx={{ mt: 4 }}>
          <CircularProgress />
        </Stack>
      )}

      {!loading && jobs.length === 0 && (
        <Paper sx={{ p: 4, borderRadius: 3, backgroundColor: "#fff" }}>
          <Typography variant="h6">No workflows yet</Typography>
          <Typography color="text.secondary" sx={{ mt: 1 }}>
            Start a RAG or Summarization workflow for this file using the
            buttons above.
          </Typography>
        </Paper>
      )}

      <Stack spacing={3}>
        {jobs.map((job) => (
          <Card
            key={job.job_id}
            sx={{
              mb: 0,
              borderRadius: 3,
              borderLeft: "6px solid",
              borderLeftColor:
                job.status === "completed"
                  ? "#4caf50"
                  : job.status === "failed"
                    ? "#d32f2f"
                    : job.status === "processing"
                      ? "#ff9800"
                      : "#90a4ae",
              overflow: "hidden",
            }}
          >
            <CardContent>
              <Stack
                direction={{ xs: "column", sm: "row" }}
                justifyContent="space-between"
                alignItems="flex-start"
                spacing={2}
              >
                <Stack spacing={1} sx={{ minWidth: 0 }}>
                  <Typography variant="h6">
                    {job.workflow_type.toUpperCase()}
                  </Typography>
                  <Chip
                    label={job.status}
                    color={
                      job.status === "completed"
                        ? "success"
                        : job.status === "failed"
                          ? "error"
                          : job.status === "processing"
                            ? "warning"
                            : "default"
                    }
                    size="small"
                  />
                  <Typography color="text.secondary" sx={{ mt: 1 }}>
                    {job.workflow_type === "summarization"
                      ? "Summary is available on the summary page once processing completes."
                      : "Open the chat after completion to interact with the RAG workflow."}
                  </Typography>
                </Stack>

                <Stack
                  direction="row"
                  spacing={1}
                  flexWrap="wrap"
                  justifyContent="flex-end"
                >
                  {job.workflow_type === "rag" && (
                    <Button
                      variant="contained"
                      href={`/workflow/v1/chat/${job.job_id}`}
                      size="small"
                    >
                      Open Chat
                    </Button>
                  )}

                  {job.workflow_type === "summarization" && (
                    <Button
                      variant="outlined"
                      href={`/workflow/v1/summary/${job.job_id}`}
                      size="small"
                    >
                      View Summary
                    </Button>
                  )}

                  {job.status === "processing" && (
                    <Button
                      color="warning"
                      variant="outlined"
                      size="small"
                      onClick={() => cancelJobHandler(job.job_id)}
                    >
                      Cancel
                    </Button>
                  )}

                  <Button
                    color="error"
                    variant="outlined"
                    size="small"
                    onClick={() => deleteJobHandler(job.job_id)}
                  >
                    Delete
                  </Button>
                </Stack>
              </Stack>
            </CardContent>
          </Card>
        ))}
      </Stack>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={5000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={alertSeverity}
          sx={{ width: "100%" }}
        >
          {alertMessage}
        </Alert>
      </Snackbar>
    </Layout>
  );
}
