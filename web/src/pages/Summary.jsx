import Layout from "../components/Layout";
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getJobStatus } from "../api/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import {
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Box,
} from "@mui/material";

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

  if (!job)
    return (
      <Layout>
        <Box sx={{ display: "flex", justifyContent: "center", mt: 10 }}>
          <CircularProgress />
        </Box>
      </Layout>
    );

  return (
    <Layout>
      <Card
        sx={{
          maxWidth: 900,
          margin: "0 auto",
          borderRadius: 3,
          boxShadow: "0 18px 55px rgba(15, 23, 42, 0.08)",
        }}
      >
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            Summary
          </Typography>

          <Box
            component="div"
            sx={{
              mt: 2,
              lineHeight: 1.8,
              color: "text.secondary",
              "& h4, & h5, & h6": {
                margin: "1rem 0 0.5rem",
                color: "#111827",
              },
              "& strong": {
                color: "#111827",
              },
              "& ul": {
                pl: 3,
                mt: 1,
              },
              "& li": {
                marginBottom: "0.35rem",
              },
              "& p": {
                margin: "0.75rem 0",
              },
            }}
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {job.result || ""}
            </ReactMarkdown>
          </Box>
        </CardContent>
      </Card>
    </Layout>
  );
}
