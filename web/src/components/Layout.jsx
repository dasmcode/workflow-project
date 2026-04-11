import { Box } from "@mui/material";
import Sidebar from "./Sidebar";

export default function Layout({ children }) {
  return (
    <Box
      sx={{ display: "flex", minHeight: "100vh", backgroundColor: "#eef3f8" }}
    >
      <Sidebar />

      <Box
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        <Box
          sx={{
            borderBottom: "1px solid rgba(15, 23, 42, 0.08)",
            px: 4,
            py: 3,
            background: "#ffffff",
            boxShadow: "0 1px 6px rgba(15, 23, 42, 0.05)",
            fontWeight: 700,
            fontSize: "18px",
          }}
        >
          Document Workflows
        </Box>

        <Box
          sx={{
            flex: 1,
            overflow: "auto",
            p: 4,
            maxWidth: 1200,
            width: "100%",
            margin: "0 auto",
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
}
