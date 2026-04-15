import Layout from "../components/Layout";
import { useParams } from "react-router-dom";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { QUERY_RAG } from "../queries/job_queries";
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Stack,
  CircularProgress,
} from "@mui/material";
import { useApolloClient } from "@apollo/client/react";

export default function Chat() {
  const { jobId } = useParams();
  const client = useApolloClient();
  const [q, setQ] = useState("");
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);

  const createId = () =>
    `msg-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

  const handleError = (id, message) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === id
          ? { ...msg, text: message, error: true, loading: false }
          : msg,
      ),
    );
  };

  const ask = async () => {
    const trimmed = q.trim();
    if (!trimmed || isStreaming) return;

    const userMessage = { id: createId(), role: "user", text: trimmed };
    const botMessage = {
      id: createId(),
      role: "bot",
      text: "",
      loading: false,
    };

    setMessages((prev) => [...prev, userMessage, botMessage]);
    setQ("");
    setIsStreaming(true);

    const observable = client.subscribe({
      query: QUERY_RAG,
      variables: { jobId, query: trimmed },
    });

    const subscription = observable.subscribe({
      next: ({ data }) => {
        const chunk = data.queryJob;
        // Update the bot message with the new chunk
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === botMessage.id
              ? { ...msg, text: msg.text + chunk, loading: false }
              : msg,
          ),
        );
      },
      error: (err) => {
        handleError(botMessage.id, err.message);
        setIsStreaming(false);
      },
      complete: () => {
        setIsStreaming(false);
      },
    });
    
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey && !isStreaming) {
      event.preventDefault();
      ask();
    }
  };

  return (
    <Layout>
      <Stack spacing={3}>
        <Paper
          sx={{
            p: 3,
            borderRadius: 3,
            backgroundColor: "#fff",
            boxShadow: "0 18px 55px rgba(15, 23, 42, 0.08)",
          }}
        >
          <Typography variant="h5" gutterBottom>
            RAG Chat
          </Typography>
          <Typography color="text.secondary">
            Ask questions about the document and receive streaming answers from
            the completed workflow.
          </Typography>
        </Paper>

        <Paper
          sx={{
            p: 3,
            minHeight: 320,
            overflowY: "auto",
            backgroundColor: "#f7fafc",
          }}
        >
          {messages.length === 0 ? (
            <Typography color="text.secondary">
              Start the conversation by asking a question.
            </Typography>
          ) : (
            <Stack spacing={2}>
              {messages.map((m) => (
                <Box
                  key={m.id}
                  sx={{
                    display: "flex",
                    justifyContent:
                      m.role === "user" ? "flex-end" : "flex-start",
                  }}
                >
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 3,
                      maxWidth: "72%",
                      bgcolor:
                        m.role === "user"
                          ? "#1976d2"
                          : m.error
                            ? "#ffebee"
                            : "#e0e0e0",
                      color:
                        m.role === "user"
                          ? "#fff"
                          : m.error
                            ? "#c62828"
                            : "#000",
                      minWidth: 80,
                    }}
                  >
                    {m.text === "" && m.role === "bot" ? (
                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 1 }}
                      >
                        <CircularProgress size={14} sx={{ color: "inherit" }} />
                        <Typography variant="body2" component="span">
                          Thinking...
                        </Typography>
                      </Box>
                    ) : m.role === "user" ? (
                      m.text
                    ) : (
                      <Box sx={{ width: "100%" }}>
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            p: ({ node, ...props }) => (
                              <Typography
                                component="p"
                                sx={{
                                  margin: 0,
                                  color: "inherit",
                                  lineHeight: 1.6,
                                }}
                                {...props}
                              />
                            ),
                            strong: ({ node, ...props }) => (
                              <Typography
                                component="strong"
                                sx={{ fontWeight: 700 }}
                                {...props}
                              />
                            ),
                            ul: ({ node, ...props }) => (
                              <Box
                                component="ul"
                                sx={{ pl: 2, mt: 1, mb: 1 }}
                                {...props}
                              />
                            ),
                            li: ({ node, ...props }) => (
                              <Box component="li" sx={{ mb: 0.5 }} {...props} />
                            ),
                          }}
                        >
                          {m.text}
                        </ReactMarkdown>
                      </Box>
                    )}
                  </Box>
                </Box>
              ))}
            </Stack>
          )}
        </Paper>

        <Box
          component={Paper}
          sx={{ p: 3, borderRadius: 3, backgroundColor: "#fff" }}
        >
          <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
            <TextField
              fullWidth
              value={q}
              onChange={(e) => setQ(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about the document..."
              disabled={isStreaming}
            />
            <Button variant="contained" onClick={ask} disabled={isStreaming}>
              {isStreaming ? "Streaming..." : "Send"}
            </Button>
          </Box>
        </Box>
      </Stack>
    </Layout>
  );
}
