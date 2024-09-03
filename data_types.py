from pydantic import BaseModel


class SignatureVerifyModel(BaseModel):
    msg_signature: str
    timestamp: str
    nonce: str
    echostr: str

class EchoSpaceModel(BaseModel):
    moodDescription: str
    themes: list
    musicTypes: list

class EchoSpaceResponseModel(BaseModel):
    success: bool
    jobID: str