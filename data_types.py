from pydantic import BaseModel


class SignatureVerifyModel(BaseModel):
    msg_signature: str
    timestamp: int
    nonce: str
    echostr: str
