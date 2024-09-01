from fastapi import APIRouter, HTTPException
import httpx
from data_types import EchoSpaceModel, EchoSpaceResponseModel

echo_space_router = APIRouter()

@echo_space_router.post("/echospace/ping")
async def ping_eqmaster(request: EchoSpaceModel):
    url = "https://echobackend-c2h9a2fsdnd7e2fz.japaneast-01.azurewebsites.net/write/"
    
    # 使用 httpx.AsyncClient 发送异步 POST 请求
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=request.dict())
            response.raise_for_status()  # 如果响应状态码不是 2xx，抛出异常

            # 打印响应内容用于调试
            print("Response Content:", response.text)

            # 尝试解析 JSON
            response_data = EchoSpaceResponseModel.parse_obj(response.json())
            return response_data.jobID
        except httpx.HTTPStatusError as http_err:
            raise HTTPException(status_code=response.status_code, detail=f"HTTP Error: {http_err}")
        except ValueError as json_err:
            raise HTTPException(status_code=500, detail=f"JSON Parsing Error: {json_err}")
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"Unexpected Error: {err}")
