from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import SessionLocal
from models import Users

router=APIRouter()
bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
@router.get("/auth")
async def auth():
    return {"message":"user is authenticated"}
class createUserRequest(BaseModel):
    email:str=Field()
    user_name:str
    first_name:str
    last_name:str
    hashed_password:str
    role:str
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency=Annotated[Session,Depends(get_db)]
@router.post("/auth/new_user_request")
async def createuser(db:db_dependency,new_user:createUserRequest):
    user_model=Users(
        email=new_user.email,
        user_name=new_user.user_name,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        hashed_password=bcrypt_context.hash(new_user.hashed_password),
        role=new_user.role,
        isactive=True
    )
    db.add(user_model)
    db.commit()