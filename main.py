import os
import json
from fastapi import FastAPI
import xml.etree.ElementTree as ET

from WXBizMsgCrypt3 import WXBizMsgCrypt
from fastapi.staticfiles import StaticFiles

from workflow_api import router as workflow_router
from onboarding.onboarding_api import router as onboarding_router
from onboarding.onboarding_api_new import router as onboarding_router_new
from network_api import router as network_router


from eq_master_api import eqmaster_router as eqmaster_router
from comic_api import comic_router as comic_router
from echo_space_api import echo_space_router as echo_space_router

from battlefield_api import router as batttlefield_router
from battlefield_agent_api import router as batttlefield_agent_router
from file_upload import file_router
from thirdparty_api import router as thirdparty_router
from text_to_voice import router as text_to_voice_router
from dotenv import load_dotenv
from login import router as login_router

from data_types import SignatureVerifyModel

import uvicorn
from fastapi.responses import RedirectResponse
import urllib.parse

load_dotenv()


sToken = os.getenv('TOKEN')
sEncodingAESKey = os.getenv('ENCODING_AES_KEY')
sCorpID = os.getenv('CORPID')

app = FastAPI()
app.include_router(eqmaster_router)

app.include_router(workflow_router)
app.include_router(onboarding_router)
app.include_router(onboarding_router_new)
app.include_router(network_router)

app.include_router(comic_router)
app.include_router(echo_space_router)

app.include_router(batttlefield_router)
app.include_router(batttlefield_agent_router)
app.include_router(file_router)
app.include_router(thirdparty_router)
app.include_router(text_to_voice_router)
app.include_router(login_router)

app.mount("/home", StaticFiles(directory="static", html=False), name="home")


def verify_signature(request: SignatureVerifyModel, i):
    if not sToken or not sEncodingAESKey or not sCorpID:
        return ""
    qy_api = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)
    if not qy_api:
        return ""
    ret, echo_str = qy_api.VerifyURL(
        request.msg_signature, request.timestamp,
        request.nonce, urllib.parse.unquote(request.echostr))
    if (ret != 0):
        print("ERR: VerifyURL ret: " + str(ret))
        return ("failed")
    else:
        print("VerifyURL success")
        return echo_str

# @app.get('/')
# @app.post('/')
# def wechat_message(
#     msg_signature: str,
#     timestamp: str,
#     nonce: str,
#     echostr: str
# ):
#     print("company_wechat begin to verify signature")
#     echo_str = verify_signature(
#         SignatureVerifyModel(msg_signature=msg_signature,
#                              timestamp=timestamp, nonce=nonce, echostr=echostr),
#         0)
#     print("company_wechat")
#     return echo_str


@app.get('/')
async def root():
    return RedirectResponse(url='/ping')


@app.get('/ping')
async def ping():
    return "version 1.1"

if __name__ == "__main__":
    # This will start the FastAPI server and allow for debugging
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
    # uvicorn.run(app, host="0.0.0.0", port=8180, log_level="debug")
