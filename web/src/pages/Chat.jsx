import Layout from "../components/Layout";
import { useParams } from "react-router-dom";
import { useState } from "react";
import { queryJob } from "../api/api";
import { Box, TextField, Button } from "@mui/material";

export default function Chat() {
  const { jobId } = useParams();
  const [q, setQ] = useState("");
  const [messages, setMessages] = useState([]);

  const ask = async () => {
    const res = await queryJob(jobId, q);

    setMessages([
      ...messages,
      { role: "user", text: q },
      { role: "bot", text: res.data.answer },
    ]);

    setQ("");
  };

  return (
    <Layout>
      <Box
        sx={{
          flex: 1,
          overflowY: "auto",
          p: 3,
        }}
      >
        {messages.map((m, i) => (
          <Box
            key={i}
            sx={{
              display: "flex",
              justifyContent: m.role === "user" ? "flex-end" : "flex-start",
              mb: 2,
            }}
          >
            <Box
              sx={{
                p: 2,
                borderRadius: 2,
                maxWidth: "60%",
                bgcolor: m.role === "user" ? "#1976d2" : "#e0e0e0",
                color: m.role === "user" ? "#fff" : "#000",
              }}
            >
              {m.text}
            </Box>
          </Box>
        ))}
      </Box>

      <Box sx={{ p: 2, borderTop: "1px solid #ddd" }}>
        <Box sx={{ display: "flex", gap: 1 }}>
          <TextField
            fullWidth
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Ask something..."
          />
          <Button variant="contained" onClick={ask}>
            Send
          </Button>
        </Box>
      </Box>
    </Layout>
  );
}
