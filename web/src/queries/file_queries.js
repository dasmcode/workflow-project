import { gql } from "@apollo/client"

export const GET_FILES = gql`
query GetFiles {
  files {
    id
    filename
  }
}
`

export const GET_FILE_BY_ID = gql`
  query GetFileById($fileId: UUID!) {
    file(fileId: $fileId) {
      ... on FileType {
        id
        filename
      }
      ... on FileErrorResponse {
        error
      }
    }
  }
`;

export const DELETE_FILE = gql`
  mutation DeleteFile($fileId: UUID!) {
    deleteFile(fileId: $fileId) {
      ... on FileSuccessResponse {
        message
      }
      ... on FileErrorResponse {
        error
      }
    }
  }
`;

export const UPLOAD_FILE = gql`
  mutation UploadFile($uploadedFile: Upload!) {
    uploadFile(uploadedFile: $uploadedFile) {
      ... on UploadFileResponse {
        fileId
      }
      ... on FileErrorResponse {
        error
      }
    }
  }
`;