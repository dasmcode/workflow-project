import { Box } from "@mui/material";
import Sidebar from "./Sidebar";

export default function Layout({ children }) {
  return (
    <Box sx={{ display: "flex", height: "100vh", backgroundColor: "#f4f6f8" }}>
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
            borderBottom: "1px solid #ddd",
            px: 4,
            py: 2,
            background: "#fff",
            fontWeight: 600,
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
            maxWidth: 1100,
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
