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
} from "@mui/material";

export default function FileDetail() {
  const { fileId } = useParams();

  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    const res = await getJobs();
    const filtered = res.data.jobs.filter((j) => j.file_id === fileId);
    setJobs(filtered);
    setLoading(false);
  };

  const runWorkflow = async (type) => {
    await executeWorkflow(fileId, type);
    loadJobs();
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
      <Stack direction="row" justifyContent="space-between" sx={{ mb: 3 }}>
        <Typography variant="h5">File: {fileId}</Typography>

        <Button color="error" variant="outlined" onClick={deleteFileHandler}>
          Delete File
        </Button>
      </Stack>

      <Stack direction="row" spacing={2} sx={{ mb: 4 }}>
        <Button variant="contained" onClick={() => runWorkflow("rag")}>
          Run RAG
        </Button>

        <Button variant="outlined" onClick={() => runWorkflow("summarization")}>
          Summarize
        </Button>
      </Stack>

      {loading && <CircularProgress />}

      {!loading && jobs.length === 0 && (
        <Typography color="text.secondary">
          No workflows yet. Start one above.
        </Typography>
      )}

      {jobs.map((job) => (
        <Card key={job.job_id} sx={{ mb: 3 }}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between">
              <Stack spacing={1}>
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
              </Stack>

              <Stack direction="row" spacing={1}>
                {job.workflow_type === "rag" && (
                  <Button
                    variant="contained"
                    href={`/workflow/v1/chat/${job.job_id}`}
                  >
                    Open Chat
                  </Button>
                )}

                {job.workflow_type === "summarization" && (
                  <Button
                    variant="outlined"
                    href={`/workflow/v1/summary/${job.job_id}`}
                  >
                    View Summary
                  </Button>
                )}

                {job.status === "processing" && (
                  <Button
                    color="warning"
                    onClick={() => cancelJobHandler(job.job_id)}
                  >
                    Cancel
                  </Button>
                )}

                <Button
                  color="error"
                  onClick={() => deleteJobHandler(job.job_id)}
                >
                  Delete
                </Button>
              </Stack>
            </Stack>
          </CardContent>
        </Card>
      ))}
    </Layout>
  );
}
