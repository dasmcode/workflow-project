import { gql } from "@apollo/client";

export const GET_JOBS_BY_FILE_ID = gql`
  query GetJobsByFileId($fileId: UUID!) {
    jobs(fileId: $fileId) {
      id
      status
      workflowType
    }
  }
`;

export const GET_JOB = gql`
  query getjob($jobId: UUID!) {
    job(jobId: $jobId) {
      ... on JobType {
        id
        result
      }
      ... on JobErrorResponse {
        error
      }
    }
  }
`;

export const EXECUTE_JOB = gql`
  mutation ExecuteWorkflow($fileId: UUID!, $workflowType: String!) {
    executeWorkflow(fileId: $fileId, workflowType: $workflowType) {
      ... on JobSuccessResponse {
        message
      }
      ... on JobErrorResponse {
        error
      }
    }
  }
`;

export const CANCEL_JOB = gql`
  mutation CancelJob($jobId: UUID!) {
    cancelJob(jobId: $jobId) {
      ... on JobSuccessResponse {
        message
      }
      ... on JobErrorResponse {
        error
      }
    }
  }
`;

export const DELETE_JOB = gql`
  mutation DeleteJobs($jobIds: [UUID!]!) {
    deleteJobs(jobIds: $jobIds) {
      ... on JobSuccessResponse {
        message
      }
      ... on JobErrorResponse {
        error
      }
    }
  }
`;

export const QUERY_RAG = gql`
  subscription Subscription($jobId: UUID!, $query: String!) {
    queryJob(jobId: $jobId, query: $query)
  }
`;
