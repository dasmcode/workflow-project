import strawberry
from uuid import UUID
from app.models.jobs import Job, JobStatus
from graphql_app.types.gql_types import JobType
from app.services.delete_job_service import delete_jobs
from app.services.retrieval import stream_response_async
from app.services.job_state import transition_job
from app.core import queue
from app.models.files import Files
from app.workers.tasks import process_step
from graphql_app.types.gql_types import return_job
from typing import Union


@strawberry.type
class JobSuccessResponse:
    message: str


@strawberry.type
class JobErrorResponse:
    error: str


@strawberry.type
class JobQuery:
    @strawberry.field
    def job(self, info: strawberry.Info, job_id: UUID) -> JobType:
        db = info.context.db
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise Exception("Job not found")
        return return_job(job)

    @strawberry.field
    def jobs(self, info: strawberry.Info) -> list[JobType]:
        db = info.context.db
        jobs = db.query(Job).all()
        return [return_job(job) for job in jobs]


@strawberry.type
class JobMutation:
    @strawberry.mutation
    def execute_workflow(
        self, info: strawberry.Info, file_id: str, workflow_type: str
    ) -> Union[JobSuccessResponse, JobErrorResponse]:
        try:
            db = info.context.db
            file = db.query(Files).filter(Files.id == file_id).first()
            if not file:
                return JobErrorResponse(error="File not found")
            existing_job = (
                db.query(Job)
                .filter(
                    Job.file_id == file_id,
                    Job.workflow_type == workflow_type,
                    Job.status == JobStatus.completed,
                )
                .first()
            )
            if existing_job:
                return JobErrorResponse(
                    error="A completed job for this file and workflow already exists"
                )
            job = Job(file_id=file_id, workflow_type=workflow_type)
            db.add(job)
            db.commit()
            db.refresh(job)
            queue.enqueue(process_step, str(job.id))
            return JobSuccessResponse(
                message=f"Workflow {workflow_type} executed successfully with job ID {job.id}"
            )
        except Exception as e:
            return JobErrorResponse(error=str(e))

    @strawberry.mutation
    def cancel_job(
        self, info: strawberry.Info, job_id: UUID
    ) -> Union[JobSuccessResponse, JobErrorResponse]:
        try:
            db = info.context.db
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise Exception("Job not found")
            if job.status in [
                JobStatus.completed,
                JobStatus.failed,
                JobStatus.cancelled,
            ]:
                raise Exception(
                    f"Cannot cancel a job that is already {job.status.value}"
                )
            transition_job(job, JobStatus.cancel_requested)
            db.commit()
            return JobSuccessResponse(
                message=f"Cancel request submitted for job with ID {job_id}"
            )
        except Exception as e:
            return JobErrorResponse(error=str(e))

    @strawberry.mutation
    def delete_job(
        self, info: strawberry.Info, job_id: UUID
    ) -> Union[JobSuccessResponse, JobErrorResponse]:
        try:
            db = info.context.db
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise Exception("Job not found")
            delete_jobs([str(job_id)])
            return JobSuccessResponse(
                message=f"Job with ID {job_id} deleted successfully"
            )
        except Exception as e:
            return JobErrorResponse(error=str(e))


@strawberry.type
class JobSubscription:
    @strawberry.subscription
    async def query_job(self, info: strawberry.Info, job_id: UUID, query: str) -> str:
        db = info.context.db
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            yield "ERROR: Job not found"
            return

        try:
            async for chunk in stream_response_async(job, query):
                yield chunk
        except Exception as e:
            yield f"ERROR: {str(e)}"
