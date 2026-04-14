import {
  Box,
  Button,
  List,
  ListItemButton,
  ListItemText,
  Typography,
  Divider,
} from "@mui/material";
import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useMutation, useQuery } from "@apollo/client/react";
import { GET_FILES,UPLOAD_FILE } from "../queries/file_queries";

export default function Sidebar() {
  const [files, setFiles] = useState([]);
  const navigate = useNavigate();
  const location = useLocation();
  const { data: Files, refetch } = useQuery(GET_FILES);
  const [uploadFileMutation] = useMutation(UPLOAD_FILE);

  useEffect(() => {
    if (Files?.files) {
      setFiles(Files.files);
    }
  }, [Files]);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    await uploadFileMutation({ variables: { uploadedFile: file } });
    refetch();
  };

  return (
    <Box
      sx={{
        width: 280,
        bgcolor: "#121318",
        color: "#fff",
        display: "flex",
        flexDirection: "column",
        p: 3,
      }}
    >
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 700 }}>
        Document Workflows
      </Typography>

      <Button
        variant="contained"
        component="label"
        sx={{ mb: 2, textTransform: "none", bgcolor: "#32343d" }}
      >
        Upload File
        <input hidden type="file" onChange={handleUpload} />
      </Button>

      <Divider sx={{ borderColor: "rgba(255,255,255,0.12)", mb: 2 }} />

      <Typography
        variant="subtitle2"
        sx={{ mb: 1, color: "rgba(255,255,255,0.72)" }}
      >
        Files ({files.length})
      </Typography>

      <List sx={{ overflowY: "auto", flex: 1, minHeight: 0 }}>
        {files.length === 0 && (
          <Typography color="rgba(255,255,255,0.6)" sx={{ p: 1 }}>
            No files uploaded yet.
          </Typography>
        )}

        {files.map((f) => (
          <ListItemButton
            key={f.id}
            onClick={() => navigate(`/file/${f.id}`)}
            selected={location.pathname === `/file/${f.id}`}
            sx={{
              borderRadius: 2,
              mb: 1,
              backgroundColor:
                location.pathname === `/file/${f.id}`
                  ? "rgba(255,255,255,0.08)"
                  : "transparent",
              "&:hover": { bgcolor: "rgba(255,255,255,0.08)" },
            }}
          >
            <ListItemText
              primary={f.filename}
              secondary={`ID: ${f.id.slice(0, 8)}`}
              slotProps={{
                primary: { noWrap: true },
                secondary: { color: "rgba(255,255,255,0.72)", fontSize: 12 },
              }}
            />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );
}
