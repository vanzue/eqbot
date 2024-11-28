import json
import thirdparty_api
from datetime import datetime
from fastapi.testclient import TestClient
from database import crud, database, schemas
from sqlalchemy.orm import Session
from fastapi import Depends
from main import app

# 创建 TestClient 实例用于调用 FastAPI 接口
client = TestClient(app)

# 加载固定评估数据集
with open("./tests/evaluation_dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

# 设置数据库连接
db = next(database.get_db())

# 结果存储
results = []

# 遍历每条记录生成回复
for record in dataset:
    product = record["product"]
    user_id = record["user_id"]
    chat_history = record["chat_history"]
    intent = record["intent"]
    print(f"Generating response for user '{user_id}' in product '{product}' with intent '{intent}'...")

    # 调用自动回复方法
    result = thirdparty_api.generate_auto_reply(product, user_id, chat_history, intent, db)
    
    if isinstance(result, dict):
        record["analysis"] = result.get("analysis", "No analysis found")
        record["suggest_response"] = result.get("response", [])
    elif isinstance(result, tuple):
        # 假设结果是元组
        record["analysis"] = result[1] if len(result) > 1 else "No analysis found"
        record["suggest_response"] = result[0] if len(result) > 0 else []
    else:
        raise TypeError(f"Unexpected result type: {type(result)}")
    
    # 将 chat_history 列表转换为字符串（例如拼接成 JSON 字符串）
    chat_history_str = json.dumps(chat_history, ensure_ascii=False)

    # 将 suggest_response 列表转换为字符串（拼接成一个长字符串）
    suggest_response_str = " ".join(record["suggest_response"])

    # 准备发送到评估接口的请求数据
    request_data = schemas.ReplyEval(
        chat_history=chat_history_str,  # 转换后的字符串
        analysis=record["analysis"],
        suggest_response=suggest_response_str  # 转换后的字符串
    )

    # 发送到评估接口并获取评估结果
    response = client.post("/evaluate_reply_eqscore", json=request_data.dict())
    
    # 确保响应成功
    if response.status_code == 200:
        eval_result = response.json()  # 获取评估结果

        # 从评估结果中提取 eval_score 和 eval_reason
        eval_score = eval_result['eval_score']
        eval_reason = eval_result['eval_reason']

        # 记录评估结果
        record["eval_score"] = eval_score
        record["eval_reason"] = eval_reason
        record["eval_time"] = datetime.utcnow().isoformat()

        # 将评估后的记录保存到结果列表中
        results.append(record)

        # 每次记录完一个结果就写入文件
        with open("generated_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

    else:
        print(f"Failed to evaluate reply for user {user_id}, product {product}.")

print("Generated test results saved to 'generated_test_results.json'.")