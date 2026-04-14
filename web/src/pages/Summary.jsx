import Layout from "../components/Layout";
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import {
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Box,
} from "@mui/material";
import { useQuery } from "@apollo/client/react";
import { GET_JOB } from "../queries/job_queries";

export default function Summary() {
  const { jobId } = useParams();
  const {data:JobData,refetch } = useQuery(GET_JOB, {
    variables: { jobId },
  })
  const [job, setJob] = useState(null);

  useEffect(() => {
    loadJob();
  }, [JobData]);

  const loadJob = async () => {
    setJob(JobData?.job);
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
