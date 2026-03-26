from pydantic import BaseModel

class WorkflowExecutionRequest(BaseModel):
    workflow_type: str
    file_id: str