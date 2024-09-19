from pydantic import BaseModel
from typing import List, Optional


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
