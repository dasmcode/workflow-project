import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000/api/v1",
});

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);

  return API.post("/upload-file/", formData);
};

export const getFiles = () => API.get("/files/");
export const deleteFile = (file_id) =>
  API.delete(`/delete-file/`, { data: { file_id } });

export const executeWorkflow = (file_id, workflow_type) =>
  API.post("/execute/", { file_id, workflow_type });

export const getJobs = () => API.get("/get-jobs/");
export const getJobStatus = (job_id) => API.get(`/job/${job_id}`);

export const cancelJob = (job_id) => API.post(`/cancel-job/`, { job_id });

export const deleteJob = (job_id) =>
  API.delete(`/delete-job/`, { data: { job_id } });

export const queryJob = (job_id, question) =>
  API.post(`/query-job/`, { job_id, query: question });

export const queryJobStream = async (job_id, question, onChunk) => {
  const response = await fetch("/api/v1/query-job/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ job_id, query: question }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Stream query failed");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      onChunk(chunk);
    }
  } finally {
    reader.releaseLock();
  }
};
