from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    description: str = None


class SignatureVerifyModel(BaseModel):
    msg_signature: str
    timestamp: int
    nonce: str
    echostr: str