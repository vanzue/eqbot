from fastapi import APIRouter, HTTPException, FastAPI, Request
import httpx

echo_space_router = APIRouter()

TARGET_SERVER_URL = "https://echobackend-c2h9a2fsdnd7e2fz.japaneast-01.azurewebsites.net/"

@echo_space_router.api_route("/echospace/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    target_url = f"{TARGET_SERVER_URL}{path}/"
    print("目标 URL:", target_url)
    print("查询参数:", request.query_params)  # 打印查询参数用于调试

    # 根据请求头中的 Content-Type 处理请求体
    content_type = request.headers.get("Content-Type", "")
    if "application/json" in content_type:
        # 处理 JSON 请求体
        request_body = await request.json()
        print("请求体 (JSON):", request_body)  # 打印请求体用于调试
        data = request_body
    elif "application/x-www-form-urlencoded" in content_type:
        # 处理表单数据
        form_data = await request.form()
        print("请求体 (表单数据):", form_data)  # 打印表单数据用于调试
        data = form_data
    else:
        # 处理原始数据
        request_body = await request.body()
        print("请求体 (原始数据):", request_body)  # 打印原始数据用于调试
        data = request_body

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            json=data if isinstance(data, dict) else None,  # 对于 JSON 格式数据，使用 json 参数
            data=None if isinstance(data, dict) else data,  # 对于表单数据或原始数据，使用 data 参数
            params=request.query_params
        )

    return response.content, response.status_code, response.headers.items()




# from fastapi import APIRouter
# from fastapi import APIRouter, HTTPException
# import httpx
# from data_types import EchoSpaceModel, EchoSpaceResponseModel

# echo_space_router = APIRouter()

# @echo_space_router.post("/echospace/{path:path}")
# async def ping_eqmaster(request: EchoSpaceModel, path: str):
#     print(path)
#     url = "https://echobackend-c2h9a2fsdnd7e2fz.japaneast-01.azurewebsites.net/write/"

#     # 使用 httpx.AsyncClient 发送异步 POST 请求
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(url, json=request.dict())
#             response.raise_for_status()  # 如果响应状态码不是 2xx，抛出异常 # 打印响应内容用于调试
#             print("Response Content:", response.text)

#             # 尝试解析 JSON
#             response_data = EchoSpaceResponseModel.parse_obj(response.json())
#             return response_data.jobID
#         except httpx.HTTPStatusError as http_err:
#             raise HTTPException(status_code=response.status_code, detail=f"HTTP Error: {http_err}")
#         except ValueError as json_err:
#             raise HTTPException(status_code=500, detail=f"JSON Parsing Error: {json_err}")
#         except Exception as err:
#             raise HTTPException(status_code=500, detail=f"Unexpected Error: {err}")