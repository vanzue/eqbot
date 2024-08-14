import os
from fastapi import FastAPI
import xml.etree.ElementTree as ET

from WXBizMsgCrypt3 import WXBizMsgCrypt
from dotenv import load_dotenv

from data_types import SignatureVerifyModel

import uvicorn
import urllib.parse

load_dotenv()


sToken = os.getenv('TOKEN')
sEncodingAESKey = os.getenv('ENCODING_AES_KEY')
sCorpID = os.getenv('CORPID')

app = FastAPI()


qy_api = [
    WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID),
]


def verify_signature(request: SignatureVerifyModel, i):
    print("verify_signature begins")
    ret, echo_str = qy_api[i].VerifyURL(
        request.msg_signature, request.timestamp,
        request.nonce, urllib.parse.unquote(request.echostr))
    if (ret != 0):
        print("ERR: VerifyURL ret: " + str(ret))
        return ("failed")
    else:
        print("VerifyURL success")
        return echo_str


@app.get('/')
@app.post('/')
def wechat_message(
    msg_signature: str,
    timestamp: str,
    nonce: str,
    echostr: str
):
    print("company_wechat begin to verify signature")
    echo_str = verify_signature(
        SignatureVerifyModel(msg_signature=msg_signature,
                             timestamp=timestamp, nonce=nonce, echostr=echostr),
        0)
    print("company_wechat")
    return echo_str


@app.get('/ping')
async def ping():
    return "version 1.1"

if __name__ == "__main__":
    # This will start the FastAPI server and allow for debugging
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
