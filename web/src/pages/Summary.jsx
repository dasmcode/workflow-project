import Layout from "../components/Layout";
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getJobStatus } from "../api/api";
import { Typography, Card, CardContent, CircularProgress } from "@mui/material";

export default function Summary() {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);

  useEffect(() => {
    loadJob();
  }, []);

  const loadJob = async () => {
    const res = await getJobStatus(jobId);
    setJob(res.data);
  };

  if (!job) return <CircularProgress />;

  return (
    <Layout>
      <Typography variant="h5" gutterBottom>
        Summary
      </Typography>

      <Card sx={{ maxWidth: 800, margin: "auto", mt: 4 }}>
        <CardContent>
          <Typography>{job.result || "No summary available"}</Typography>
        </CardContent>
      </Card>
    </Layout>
  );
}
