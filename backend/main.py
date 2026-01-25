from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
import shutil
from zip_file_extracter.zip_extracting import extract_zip, parse_messages, clean_extract_dir, UPLOAD_DIR, EXTRACT_DIR
from openai_listener.openai_helper import ask_gpt
from database import engine, SessionLocal
import models
from models import Zipfiles, User, Chat
from schemas import AnalysisResult
from typing import Annotated
from sqlalchemy.orm import Session
import auth
from auth import get_current_user

app = FastAPI()
app.include_router(auth.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@app.get("/email-and-id", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return {"User": user}



#below is for whatsapp

@app.post("/analyze_with_zip", response_model=AnalysisResult)
async def analyze_chat(uploaded_zip: UploadFile = File(...), instruction: str = Form(...), platform: str = Form(...), user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # File must be ZIP
    if not uploaded_zip.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP files allowed")
    # Clean previous extraction
    clean_extract_dir()
    # Save ZIP in uploads/
    zip_path = UPLOAD_DIR / uploaded_zip.filename
    with zip_path.open("wb") as buffer:
        shutil.copyfileobj(uploaded_zip.file, buffer)
    # Extract ZIP in extracted/
    extract_zip(zip_path)
    # Parse messages
    chat_text = parse_messages(EXTRACT_DIR)
    # Save friend name and chat to DB
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    friend_name = uploaded_zip.filename.strip(".zip")
    db.add(Zipfiles(content=chat_text, user_id=user['id'], friend_name=friend_name))
    db.commit()
    
    zipname = uploaded_zip.filename
    # Ask GPT
    gpt_response = ask_gpt(chat_text, instruction)
    
    chat = Chat(user_id=user['id'], title=zipname, response=gpt_response)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return {"title": zipname, "response": gpt_response, "chat_id": chat.id}

@app.post("/analyze_without_zip", response_model=AnalysisResult)
async def analyze_chat_without_zip(friendname: str, instruction: str, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    # Retrieve last chat from DB
    zipfile_entry = db.query(Zipfiles.content).where(Zipfiles.user_id == user['id'], Zipfiles.friend_name == friendname)
    if not zipfile_entry:
        raise HTTPException(status_code=400, detail="No chat history found for user")
    chat_text = zipfile_entry[0].content
    # Ask GPT
    gpt_response = ask_gpt(chat_text, instruction)
    return AnalysisResult(response_from_gpt=gpt_response)

#list of friends for the logged-in user for displaying on frontend
@app.get("/friend-list", status_code=status.HTTP_200_OK)
async def friend_list(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    zipfiles = db.query(Zipfiles).filter(Zipfiles.user_id == user['id']).all()
    friends = [zf.friend_name for zf in zipfiles]
    return {"friends": friends}

@app.get("/chats")
def get_chats(user: user_dependency, db: db_dependency):
    chats = (db.query(Chat).filter(Chat.user_id == user['id']).order_by(Chat.id.desc()).all())
    return [{"id": chat.id, "title": chat.title, "response": chat.response} for chat in chats]

#below is for instagram

#below is for telegram