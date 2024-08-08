import os
from flask import Flask, request
import xml.etree.ElementTree as ET

from WXBizMsgCrypt3 import WXBizMsgCrypt
from dotenv import load_dotenv

load_dotenv()


sToken = os.getenv('TOKEN')
sEncodingAESKey = os.getenv('ENCODING_AES_KEY')
sCorpID = os.getenv('CORP_ID')

app = Flask(__name__)


qy_api = [
    WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID),
]  # 对应接受消息回调模式中的token，EncodingAESKey 和 企业信息中的企业id

# 开启消息接受模式时验证接口连通性


def signature(request, i):
    msg_signature = request.args.get('msg_signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    echo_str = request.args.get('echostr', '')
    ret, sEchoStr = qy_api[i].VerifyURL(
        msg_signature, timestamp, nonce, echo_str)
    if (ret != 0):
        print("ERR: VerifyURL ret: " + str(ret))
        return ("failed")
    else:
        return (sEchoStr)


@app.route('/company_wechat', methods=['GET', 'POST'])
def company_wechat():
    echo_str = signature(request, 0)
    print("company_wechat")
    return (echo_str)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
