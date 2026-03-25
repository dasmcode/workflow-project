from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # Process the file contents as needed
    return {"filename": file.filename, "content_type": file.content_type, "size": len(contents)}