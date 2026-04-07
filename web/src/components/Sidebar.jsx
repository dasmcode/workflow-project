import {
  Box,
  Button,
  List,
  ListItemButton,
  ListItemText,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import { getFiles, uploadFile } from "../api/api";
import { useNavigate } from "react-router-dom";

export default function Sidebar() {
  const [files, setFiles] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    const res = await getFiles();
    setFiles(res.data.files); 
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    await uploadFile(file);
    loadFiles();
  };

  return (
    <Box
      sx={{
        width: 260,
        bgcolor: "#202123",
        color: "#fff",
        display: "flex",
        flexDirection: "column",
        p: 2,
      }}
    >
      <Button
        variant="contained"
        component="label"
        sx={{ mb: 2, bgcolor: "#444654" }}
      >
        Upload
        <input hidden type="file" onChange={handleUpload} />
      </Button>

      <Typography variant="subtitle2" sx={{ mb: 1 }}>
        Files
      </Typography>

      <List sx={{ overflowY: "auto" }}>
        {files.map((f) => (
          <ListItemButton
            key={f.file_id}
            onClick={() => navigate(`/file/${f.file_id}`)}
            sx={{
              borderRadius: 1,
              mb: 1,
              "&:hover": { bgcolor: "#2a2b32" },
            }}
          >
            <ListItemText
              primary={f.filename}
              secondary={f.file_id.slice(0, 6)}
            />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );
}
