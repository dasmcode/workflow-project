from pydantic import BaseModel

class WorkflowExecutionRequest(BaseModel):
    workflow_type: str
    file_id: str
    
class QueryRequest(BaseModel):
    job_id: str
    query: str
    
class JobPayload(BaseModel):
    job_id: str
    
class FilePayload(BaseModel):
    file_id: str