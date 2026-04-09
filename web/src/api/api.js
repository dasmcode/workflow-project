import axios from "axios";

const API = axios.create({
  baseURL: "/api/v1",
});

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);

  return API.post("/upload-file/", formData);
};

export const getFiles = () => API.get("/files/");
export const deleteFile = (file_id) => API.delete(`/delete-file/`, { data: { file_id } });

export const executeWorkflow = (file_id, workflow_type) =>
  API.post("/execute/", { file_id, workflow_type });

export const getJobs = () => API.get("/get-jobs/");
export const getJobStatus = (job_id) => API.get(`/job/${job_id}`);

export const cancelJob = (job_id) => API.post(`/cancel-job/`, { job_id });

export const deleteJob = (job_id) => API.delete(`/delete-job/`, { data: { job_id } });

export const queryJob = (job_id, question) =>
  API.post(`/query-job/`, { job_id, query: question });
