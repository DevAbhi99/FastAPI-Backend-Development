from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy import text
from enum import IntEnum
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

#load env variables
load_dotenv()


api=FastAPI()

#middleware
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

api.add_middleware(
GZipMiddleware, minimum_size=1000
)


#Setting up mysql url

dbPwd=os.getenv("DB_PASSWORD")

password=quote_plus(f"{dbPwd}")

mysql_url=f'mysql+pymysql://root:{password}@localhost:3306/fastapidb'

engine=create_engine(mysql_url, echo=True)

#Priority class
class Priority(IntEnum):
    high=3
    medium=2
    low=1


#User class
class User(SQLModel, table=True):
    __tablename__='users'
    id:int|None=Field(default=None, primary_key=True)
    name:str=Field(nullable=False)
    age:int=Field(nullable=False)
    priority:Priority=Field(nullable=False)


#REST API methods

#get method
@api.get('/getData')
def getData():
    with Session(engine) as session:
        users=session.exec(select(User)).all()
        return users
    
#post method    
@api.post('/sendData')
def postData(newuser:User):
    with Session(engine) as session:
        session.add(newuser)
        session.commit()
        session.refresh(newuser)
        return {'message':'Data inserted successfully'}

#put method    
@api.put('/updateData/{id}')
def updateData(id:int, newuser:User):
    with Session(engine) as session:
        user=session.get(User, id)

        if not user:
            raise HTTPException(status_code=404, detail='Wrong input')
        
        user.name=newuser.name
        user.age=newuser.age
        user.priority=newuser.priority
        
        session.add(user)
        session.commit()
        session.refresh(user)
        return {'message':'Data updated successfully'}
    
#delete method
@api.delete('/deleteData/{id}')
def deleteData(id:int):
    with Session(engine) as session:
        user=session.get(User, id)

        if not user:
            raise HTTPException(status_Code=404, detail='wrong operation')
        
        session.delete(user)
        session.commit()
        return {'message':'Data deleted successfully'}
    

#clear method
@api.delete('/clearData')
def clearData():
    with Session(engine) as session:
        session.exec(text('truncate table users;'))
        session.commit()
        return {'message':'Data cleared successfully'}
