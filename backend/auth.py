from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import User
from schemas import RegisterUserRequest, Token
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

router = APIRouter(
    prefix="/auth",
    tags=["authorization"], #just naming, doesnt matter
)

SECRET_KEY = 'lol'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login-to-get-token') #tokenUrl is the endpoint where user will get the token
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)] #receive database session as dependency that further we will call as db

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(db: db_dependency,
                      registering_user: RegisterUserRequest):
    new_user = User(email=registering_user.email, hashed_password=bcrypt_context.hash(registering_user.password))
    
    db.add(new_user)
    db.commit()
    
@router.post("/login-to-get-token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    token = create_access_token(user.email, user.id, timedelta(minutes=30))
    
    return {'access_token': token, 'token_type': 'bearer'}


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.email == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        user_id: int = payload.get('id')
        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return {'email': email, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')