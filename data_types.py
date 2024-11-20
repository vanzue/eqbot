from pydantic import BaseModel
from typing import List, Optional, Dict

class CreateUserRequest(BaseModel):
    name: str
    source: str
    unique_id: str
    gender: str
    job_level: str
    issues: str
    job_id: str

class SignatureVerifyModel(BaseModel):
    msg_signature: str
    timestamp: str
    nonce: str
    echostr: str

class ContactProfileCreate(BaseModel):
    personal_name: str
    name: str
    tag: Optional[str]
    contact_relationship : Optional[str]


class ChatCreate(BaseModel):
    personal_name: str
    name: Optional[str] = None
    contact_id: Optional[int] = None
    chat_content: str
    tag: Optional[str] = None
    contact_relationship: Optional[str] = None


class Choice(BaseModel):
    choice: int
    job_id: str

class EchoSpaceModel(BaseModel):
    moodDescription: str
    themes: list
    musicTypes: list

class EchoSpaceResponseModel(BaseModel):
    success: bool
    jobID: str

class BattlefieldRequest(BaseModel):
    person_id: int
    course_id: int
    chat_content: str
    locale: str = "zh"

class BattlefieldEval(BaseModel):
    person_id: int
    course_id: int
    chat_content: str
    status: str
    result: int
    person_star: int
    locale: str = "zh"

class DiamondUpdate(BaseModel):
    person_id: int
    num_diamond: int

class ScenarioRequest(BaseModel):
    scenario_id: int
    choices: str # eg.11,21
    locale: Optional[str]

class AnalysisData(BaseModel):
    background: str
    description: str
    choice: str
    analysis: str

class ScenarioFinal(BaseModel):
    scores: Dict[str, int] # dimension name: score
    job_id: str
    dialogue_history: List[AnalysisData] # 不能有{}和”
    locale: Optional[str] = None