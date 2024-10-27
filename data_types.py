from pydantic import BaseModel
from typing import List, Optional, Dict


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
    lang_type: str = "zh"

class BattlefieldEval(BaseModel):
    person_id: int
    course_id: int
    chat_content: str
    status: str
    result: int
    person_star: int
    lang_type: str = "zh"

class DiamondUpdate(BaseModel):
    person_id: int
    num_diamond: int

class ScenarioRequest(BaseModel):
    scenario_id: int
    choices: str
    locale: Optional[str]

class ScenarioFinal(BaseModel):
    scores: List[int]
    job_id: str
    dialogue_history: List[Dict[str, str]]
    locale: Optional[str] = None