from typing import List, Optional
from pydantic import BaseModel, EmailStr
class RegisterRequest(BaseModel):
    full_name:str
    email:EmailStr
    password:str
class LoginRequest(BaseModel):
    email:EmailStr
    password:str
class StartExamRequest(BaseModel):
    user_id:int
    track:str
    level:int
class AnswerSubmission(BaseModel):
    question_id:int
    selected_option:str
class SubmitExamRequest(BaseModel):
    attempt_id:int
    answers:List[AnswerSubmission]
    essay_response:Optional[str]=None
    scenario_response:Optional[str]=None
class RetakeRequest(BaseModel):
    user_id:int
    source_attempt_id:int
