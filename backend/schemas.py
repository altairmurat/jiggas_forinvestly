from pydantic import BaseModel

class AnalysisResult(BaseModel):
    chat_id: int
    title: str
    response: str

class RegisterUserRequest(BaseModel):
    email: str
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str