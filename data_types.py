from pydantic import BaseModel


class SignatureVerifyModel(BaseModel):
    msg_signature: str
    timestamp: str
    nonce: str
    echostr: str
