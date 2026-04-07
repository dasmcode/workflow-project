import Layout from "../components/Layout";
import { useParams, useNavigate } from "react-router-dom";
import { executeWorkflow, getJobs } from "../api/api";
import { useEffect, useState } from "react";
import { Button, Typography, Card, CardContent } from "@mui/material";

export default function FileDetail() {
  const { fileId } = useParams();
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    const res = await getJobs();
    const data = res.data.jobs;
    setJobs(data.filter((j) => j.file_id === fileId));
  };

  const runWorkflow = async (type) => {
    await executeWorkflow(fileId, type);
    loadJobs();
  };

  return (
    <Layout>
      <Typography variant="h5">File: {fileId}</Typography>

      <Button onClick={() => runWorkflow("rag")}>Run RAG</Button>
      <Button onClick={() => runWorkflow("summarization")}>Summarize</Button>

      {jobs.map((job) => (
        <Card key={job.id} sx={{ mt: 2 }}>
          <CardContent>
            <Typography variant="subtitle1">
              {job.workflow_type.toUpperCase()}
            </Typography>

            <Typography color="text.secondary">Status: {job.status}</Typography>

            {job.workflow_type === "rag" ? (
              <Button
                variant="contained"
                sx={{ mt: 1 }}
                onClick={() => navigate(`/chat/${job.job_id}`)}
              >
                Open Chat
              </Button>
            ) : (
              <Button
                variant="outlined"
                sx={{ mt: 1 }}
                onClick={() => navigate(`/summary/${job.job_id}`)}
              >
                View Summary
              </Button>
            )}
          </CardContent>
        </Card>
      ))}
    </Layout>
  );
}
