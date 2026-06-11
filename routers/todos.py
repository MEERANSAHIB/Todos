from fastapi import APIRouter
router = APIRouter()
from fastapi import FastAPI, Depends, status, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status

from database import Base, SessionLocal,engine
from models import ToDos
from routers import auth
app=FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency=Annotated[Session,Depends(get_db)]

@router.get("/auth")
async def auth():
    return {"message": "user is authenticated"}


@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency ):
    return db.query(ToDos).all()
@router.get("/todos/{todo_id}",status_code=status.HTTP_200_OK)
async def read_todobyid(db: db_dependency,todo_id:int = Path(gt=0)):
    todo_model=db.query(ToDos).filter(ToDos.Id == todo_id).first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code=404,detail="Not Found")
class ToDoRequest(BaseModel):
    title:str=Field(min_length=1,max_length=15)
    description:str=Field(min_length=1,max_length=150)
    priority:int=Field(gt=0,le=5)
    complete:bool=Field(default=False)
@router.post("/todos/new_todo",status_code=status.HTTP_201_CREATED)
async def new_todo(db: db_dependency,new_input:ToDoRequest):
    todo_model=ToDos(**new_input.model_dump())
    db.add(todo_model)
    db.commit()
@router.put("/todos/alter/{todo_id}")
async def alter_todo(db: db_dependency,todorequest:ToDoRequest,todo_id:int=Path(ge=1)):
    todo_model=db.query(ToDos).filter(ToDos.Id==todo_id).first()
    if todo_model is not None:
        todo_model.title=todorequest.title
        todo_model.description=todorequest.description
        todo_model.priority=todorequest.priority
        todo_model.complete=todorequest.complete
        db.add(todo_model)
        db.commit()
    else:
        raise HTTPException(status_code=404,detail="Not Found")
@router.delete("/todos/delete_todo/{to_do_id}")
async def delete_todo(db: db_dependency,to_do_id:int=Path(gt=0)):
    todo_model=db.query(ToDos).filter(ToDos.id==to_do_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="Not found")
    db.query(ToDos).filter(ToDos.id == to_do_id).delete()
    db.commit()