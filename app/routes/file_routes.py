import os

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.utils.file_handler import save_file
from app.models.files import Files
router = APIRouter()

@router.post("/upload-file/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        file_path,file_id = save_file(contents,file.filename)
        file = Files(id=file_id,filename=file.filename, filepath=file_path)
        db.add(file)
        db.commit()
        db.refresh(file)
        return JSONResponse(content={"file_id": file_id, "file_path": file_path},status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)},status_code=500)
    

@router.get("/file/{file_id}")
def get_file(file_id:str, db:Session = Depends(get_db)):
    try:
        file = db.query(Files).filter(Files.id == file_id).first()
        if not file:
            return JSONResponse(content={"error": "File not found"}, status_code=404)
        return JSONResponse(content={"file_id": str(file.id), "filename": file.filename, "filepath": file.filepath, "created_at": str(file.created_at)}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@router.get("/files/")
def get_all_files(db:Session = Depends(get_db)):
    try:
        files = db.query(Files).all()
        file_list = [{"file_id": str(file.id), "filename": file.filename, "filepath": file.filepath, "created_at": str(file.created_at)} for file in files]
        return JSONResponse(content={"files": file_list}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@router.delete("/delete-file/{file_id}")
def delete_file(file_id:str, db:Session = Depends(get_db)):
    try:
        file = db.query(Files).filter(Files.id == file_id).first()
        file_path = file.filepath
        if os.path.exists(file_path):
            os.remove(file_path)
        if not file:
            return JSONResponse(content={"error": "File not found"}, status_code=404)
        db.delete(file)
        db.commit()
        return JSONResponse(content={"message": f"File with ID {file_id} deleted successfully"}, status_code=200)
    except Exception as e:
        db.rollback()
        return JSONResponse(content={"error": str(e)}, status_code=500)
