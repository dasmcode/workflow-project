import strawberry
from strawberry.file_uploads import Upload
from uuid import UUID
from app.models.jobs import Job
from app.models.files import Files
from graphql_app.types.gql_types import FileType
import os
from app.services.delete_job_service import delete_jobs
from app.utils.file_handler import save_file
from graphql_app.types.gql_types import return_file


@strawberry.type
class UploadFileResponse:
    file_id: UUID
    file_path: str


@strawberry.type
class FileQuery:
    @strawberry.field
    def file(self, info: strawberry.Info, file_id: UUID) -> FileType:
        db = info.context.db
        file = db.query(Files).filter(Files.id == file_id).first()
        if not file:
            raise Exception("File not found")
        return return_file(file)

    @strawberry.field
    def files(self, info: strawberry.Info) -> list[FileType]:
        db = info.context.db
        files = db.query(Files).all()
        return [return_file(file) for file in files]


@strawberry.type
class FileMutation:
    @strawberry.mutation
    async def upload_file(
        self, info: strawberry.Info, uploaded_file: Upload
    ) -> UploadFileResponse:
        db = info.context.db
        contents = await uploaded_file.read()
        file_path, file_id = save_file(contents, uploaded_file.filename)
        file = Files(id=file_id, filename=uploaded_file.filename, filepath=file_path)
        db.add(file)
        db.commit()
        db.refresh(file)
        return UploadFileResponse(file_id=file_id, file_path=file_path)

    @strawberry.mutation
    def delete_file(self, info: strawberry.Info, file_id: UUID) -> str:
        db = info.context.db
        file = db.query(Files).filter(Files.id == file_id).first()
        if not file:
            raise Exception("File not found")
        jobs = db.query(Job).filter(Job.file_id == file_id).all()
        job_ids = [str(job.id) for job in jobs]
        delete_jobs(job_ids)
        file_path = file.filepath
        if os.path.exists(file_path):
            os.remove(file_path)
        db.delete(file)
        db.commit()
        return f"File with ID {str(file_id)} deleted successfully"
