from strawberry.fastapi import BaseContext
from app.core.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

class Context(BaseContext):
    def __init__(self, db: Session):
        self.db = db

async def get_context(db: Session = Depends(get_db)):
    return Context(db=db)