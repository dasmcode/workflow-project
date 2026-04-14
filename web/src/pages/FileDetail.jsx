import Layout from "../components/Layout";
import { useNavigate, useParams } from "react-router-dom";
import { useEffect, useState } from "react";

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
import { useMutation, useQuery } from "@apollo/client/react";
import { DELETE_FILE } from "../queries/file_queries";
import {
  GET_JOBS_BY_FILE_ID,
  EXECUTE_JOB,
  CANCEL_JOB,
  DELETE_JOB,
} from "../queries/job_queries";

export default function FileDetail() {
  const navigate = useNavigate();
  const { fileId } = useParams();

  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [alertMessage, setAlertMessage] = useState("");
  const [alertSeverity, setAlertSeverity] = useState("success");
  const [snackbarOpen, setSnackbarOpen] = useState(false);

  const [deleteFileMutation] = useMutation(DELETE_FILE);
  const [executeWorkflowMutation] = useMutation(EXECUTE_JOB);
  const [cancelJobMutation] = useMutation(CANCEL_JOB);
  const [deleteJobMutation] = useMutation(DELETE_JOB);
  const { data: JobsData, refetch } = useQuery(GET_JOBS_BY_FILE_ID, {
    variables: { fileId },
  });

  useEffect(() => {
    loadJobs();
  }, [JobsData]);

  const loadJobs = async () => {
    setLoading(true);
    setJobs(JobsData?.jobs || []);
    setLoading(false);
  };

  const runWorkflow = async (type) => {
    setActionLoading(true);

    try {
      const response = await executeWorkflowMutation({
        variables: {
          fileId,
          workflowType: type,
        },
      });
      console.log("Execute workflow response data:", response);
      const responseData = response.data.executeWorkflow;
      if (responseData?.error) {
        throw new Error(responseData.error);
      }
      setAlertSeverity("success");
      setAlertMessage(responseData?.message || `Started ${type} workflow`);
      setSnackbarOpen(true);
    } catch (error) {
      const message =
        error?.response?.data?.error ||
        error?.message ||
        "Unable to execute workflow";
      setAlertSeverity("error");
      setAlertMessage(message);
      setSnackbarOpen(true);
    } finally {
      await refetch();
      setActionLoading(false);
    }
  };

  const handleCloseSnackbar = (_, reason) => {
    if (reason === "clickaway") return;
    setSnackbarOpen(false);
  };

  const cancelJobHandler = async (jobId) => {
    setActionLoading(true);
    try {
      const response = await cancelJobMutation({
        variables: { jobId },
      });
      const responseData = response.data.cancelJob;
      if (responseData?.error) {
        throw new Error(responseData.error);
      }
      setAlertSeverity("info");
      setAlertMessage(responseData?.message || `Job cancelled successfully`);
      setSnackbarOpen(true);
    } catch (error) {
      const message =
        error?.response?.data?.error ||
        error?.message ||
        "Unable to cancel job";
      setAlertSeverity("error");
      setAlertMessage(message);
      setSnackbarOpen(true);
    } finally {
      await refetch();
      setActionLoading(false);
    }
  };

  const deleteJobHandler = async (jobIds) => {
    setActionLoading(true);
    try {
      const response = await deleteJobMutation({
        variables: { jobIds },
      });
      const responseData = response.data.deleteJob;
      if (responseData?.error) {
        throw new Error(responseData.error);
      }
      setAlertSeverity("info");
      setAlertMessage(responseData?.message || `Job deleted successfully`);
      setSnackbarOpen(true);
    } catch (error) {
      const message =
        error?.response?.data?.error ||
        error?.message ||
        "Unable to delete job";
      setAlertSeverity("error");
      setAlertMessage(message);
      setSnackbarOpen(true);
    } finally {
      await refetch();
      setActionLoading(false);
    }
  };

  const deleteFileHandler = async () => {
    deleteFileMutation({ variables: { fileId } });
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
            key={job.id}
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
                    {job.workflowType.toUpperCase()}
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
                    {job.workflowType === "summarization"
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
                  {job.workflowType === "rag" && (
                    <Button
                      variant="contained"
                      size="small"
                      onClick={() => navigate(`/chat/${job.id}`)}
                    >
                      Open Chat
                    </Button>
                  )}

                  {job.workflowType === "summarization" && (
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => navigate(`/summary/${job.id}`)}
                    >
                      View Summary
                    </Button>
                  )}

                  {job.status === "processing" && (
                    <Button
                      color="warning"
                      variant="outlined"
                      size="small"
                      onClick={() => cancelJobHandler(job.id)}
                    >
                      Cancel
                    </Button>
                  )}

                  <Button
                    color="error"
                    variant="outlined"
                    size="small"
                    onClick={() => deleteJobHandler([job.id])}
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
