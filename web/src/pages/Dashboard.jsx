import Layout from "../components/Layout";
import { Typography, Paper, Box } from "@mui/material";

export default function Dashboard() {
  return (
    <Layout>
      <Paper
        sx={{
          p: 4,
          borderRadius: 3,
          boxShadow: "0 18px 55px rgba(15, 23, 42, 0.08)",
          backgroundColor: "#fff",
        }}
      >
        <Typography variant="h4" gutterBottom>
          Welcome to Document Workflows
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 2 }}>
          Select a file from the left sidebar or upload a new document to start
          generating RAG workflows and summaries.
        </Typography>
        <Typography color="text.secondary">
          Completed workflows cannot be repeated for the same file.
        </Typography>
      </Paper>
    </Layout>
  );
}
