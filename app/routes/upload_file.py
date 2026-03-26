from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from app.utils.file_handler import save_file
router = APIRouter()

@router.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        file_id, file_path = save_file(contents,file.filename)
        return JSONResponse(content={"file_id": file_id, "file_path": file_path},status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)},status_code=500)