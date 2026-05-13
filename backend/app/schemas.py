from typing import List, Optional
from pydantic import BaseModel, EmailStr
class RegisterRequest(BaseModel):
    full_name:str
    email:EmailStr
    password:str
class LoginRequest(BaseModel):
    email:EmailStr
    password:str
class DevReadyLaunchRequest(BaseModel):
    full_name:str
    email:EmailStr
    profile_id:Optional[str]=None
    badge_role:Optional[str]=None
    badge_role_key:Optional[str]=None
    badge_level:Optional[str]=None
    badge_title:Optional[str]=None
    exam_id:Optional[str]=None
    exam_version:Optional[str]=None
    certificate_id:Optional[str]=None
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
