import Layout from "../components/Layout";
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getJobStatus } from "../api/api";

import { Card, CardContent, Typography, CircularProgress } from "@mui/material";

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
      <Card sx={{ maxWidth: 900, margin: "0 auto" }}>
        <CardContent>
          <Typography variant="h6">Summary</Typography>

          <Typography
            sx={{
              mt: 2,
              whiteSpace: "pre-line",
              lineHeight: 1.6,
            }}
          >
            {job.result}
          </Typography>
        </CardContent>
      </Card>
    </Layout>
  );
}
