from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import os
import random
import json

import data_types
from database import crud, database, schemas
from llm.profile_eval import process_with_llm_new
from llm.profile_eval_en import process_with_llm_en_new

router = APIRouter()

# 定义文件名
filename = ["scenario_1", "scenario_2", "scenario_3", "scenario_4", "scenario_5", 
            "scenario_6", "scenario_7", "scenario_8", "scenario_9", "scenario_10"]
filename_en = ["scenario_1_en", "scenario_2_en", "scenario_3_en", "scenario_4_en"]

def get_random_scenario(locale: Optional[str]):
    """
    根据 locale 随机选择一个场景并返回文件路径
    """
    if locale == "en":
        scenario_id = random.randrange(1, len(filename_en))
        # print(scenario_id)
        folder = os.path.join("onboarding", filename_en[scenario_id])
    else:
        scenario_id = random.randrange(0, len(filename))
        folder = os.path.join("onboarding", filename[scenario_id])
    return folder, scenario_id + 1

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail=f"文件 {filepath} 不是有效的 JSON 格式。")
    except IOError:
        raise HTTPException(status_code=404, detail=f"无法读取文件 {filepath}。")

@router.post("/initialize_scenario")
async def initialize_scenario(locale: Optional[str] = None):
    """
    根据 locale 初始化场景，随机返回一个场景和其ID
    """
    folder, scenario_id = get_random_scenario(locale)
    scene = load_json(os.path.join(folder, "branch_.json"))
    return {"scene": scene, "scenario_id": scenario_id}

@router.post("/retrieve_scene")
async def retrieve_scene(request: data_types.ScenarioRequest):
    """
    接收用户选择列表，根据选择路径返回对应的场景 JSON 文件
    """
    locale = request.locale
    if locale == "en":
        folder = os.path.join("onboarding", f"scenario_{request.scenario_id}_en")
    else:
        folder = os.path.join("onboarding", f"scenario_{request.scenario_id}")

    branch = request.choices
    filepath = os.path.join(folder, f"branch_{branch}.json")

    scene = load_json(filepath)
    return {"scene": scene, "scenario_id": request.scenario_id}

@router.post("/finalize_scenario")
async def finalize_scenario(
    request: data_types.ScenarioFinal,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
):
    """
    接收最终分数和对话记录，并通过LLM分析返回结果
    """
    locale = request.locale
    job_id = request.job_id
    scores = request.scores
    dialogue_history = request.dialogue_history

    background_tasks.add_task(background_process_data, locale, job_id, scores, dialogue_history, db)

    return {"message": "Processing data in background"}

async def background_process_data(locale: str, job_id: str, scores: list, dialogue_history: str, db: Session = Depends(database.get_db),):
    # 异步调用 LLM 分析
    if locale != "en":
        response = await process_with_llm_new(scores, dialogue_history)
    else:
        response = await process_with_llm_en_new(scores, dialogue_history)

    # 更新数据库
    min_score_key = min(scores, key=scores.get)
    dimension_keys = list(scores.keys())  # 获取 scores 的键的列表
    min_score_idx = dimension_keys.index(min_score_key)
    tags = ["超绝顿感力", "情绪小火山", "职场隐士", "交流绝缘体", "交流绝缘体"] if locale != "en" else ["Perception", "Self Regulation", "Empathy", "Social Skill", "Motivation"]
    tag_description = ["超绝顿感力tag_description", "情绪小火山tag_description", "职场隐士tag_description", "交流绝缘体tag_description", "交流绝缘体tag_description"] if locale != "en" else ["tag_description0", "tag_description1", "tag_description2", "tag_description3", "tag_description4"]

    personal_info = crud.get_personal_info_by_job_id(db, job_id)
    personal_info_update = schemas.PersonalInfoUpdate(
        tag=tags[min_score_idx],
        tag_description=tag_description[min_score_idx]
    )
    updated_personal_info = crud.update_personal_info_by_name(db, personal_info.name, personal_info_update)

    # 创建 EQ 分数记录
    eq_score_data = schemas.EQScoreCreate(
        job_id=job_id,
        person_id=personal_info.id,
        dimension1_score=response["dimension1_score"],
        dimension1_detail=response["dimension1_detail"],
        dimension2_score=response["dimension2_score"],
        dimension2_detail=response["dimension2_detail"],
        dimension3_score=response["dimension3_score"],
        dimension3_detail=response["dimension3_detail"],
        dimension4_score=response["dimension4_score"],
        dimension4_detail=response["dimension4_detail"],
        dimension5_score=response["dimension5_score"],
        dimension5_detail=response["dimension5_detail"],
        summary=response["summary"],
        detail=response["detail"],
        detail_summary=response['detail_summary'],
        overall_suggestion=response["overall_suggestion"]
    )
    eq_score = crud.create_eq_score(db, eq_score_data)
    print("llm 分析完成")