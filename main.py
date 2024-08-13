import os
from fastapi import FastAPI
import xml.etree.ElementTree as ET

from WXBizMsgCrypt3 import WXBizMsgCrypt
from dotenv import load_dotenv

from data_types import SignatureVerifyModel

import uvicorn

load_dotenv()


sToken = os.getenv('TOKEN')
sEncodingAESKey = os.getenv('ENCODING_AES_KEY')
sCorpID = os.getenv('CORPID')

app = FastAPI()


qy_api = [
    WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID),
]


def verify_signature(request: SignatureVerifyModel, i):
    ret, echo_str = qy_api[i].VerifyURL(
        request.msg_signature, request.timestamp,
        request.nonce, request.echo_str)
    if (ret != 0):
        print("ERR: VerifyURL ret: " + str(ret))
        return ("failed")
    else:
        return echo_str


@app.get('/ack')
def ack_alive(
    msg_signature: str,
    timestamp: int,
    nonce: str,
    echostr: str
):
    echo_str = verify_signature(
        SignatureVerifyModel(msg_signature, timestamp, nonce, echostr),
        0)
    print("company_wechat")
    return echo_str


@app.get('/ping')
async def ping():
    return "true"

if __name__ == "__main__":
    # This will start the FastAPI server and allow for debugging
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
