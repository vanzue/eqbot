from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json
import os
from typing import List, Dict, Optional
import random

from database import crud, database, schemas
from llm.profile_eval import process_with_llm
from llm.profile_eval_en import process_with_llm_en
from data_types import Choice

router = APIRouter()

def load_json_files_to_dict(base_folder):
    json_data = {}
    
    for root, dirs, files in os.walk(base_folder):
        if os.path.basename(root).startswith("scenario_"):
            for file_name in files:
                if file_name.endswith(".json"):
                    file_path = os.path.join(root, file_name)
                    #relative_path = os.path.relpath(full_file_path, base_folder)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            json_data[file_path] = json.load(f)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in file {file_path}: {e}")
                    except IOError as e:
                        print(f"Error reading file {file_path}: {e}")
    return json_data

all_scenario_data = load_json_files_to_dict("onboarding")


class ScenarioManager:
    def __init__(self, scenario_id: Optional[int] = None, locale: Optional[str] = None):
        self.current_branch = ""
        self.locale = locale
        # self.folder = self.get_latest_scenario_folder()
        self.filename = ["scenario_1", "scenario_2",
                         "scenario_3", "scenario_4",
                         "scenario_5", "scenario_6",
                         "scenario_7", "scenario_8", 
                         "scenario_9", "scenario_10"]
        self.filename_en = ["scenario_1_en", "scenario_2_en",
                         "scenario_3_en", "scenario_4_en"]
        
        # self.scenario_id = scenario_id if scenario_id is not None else random.randrange(0, len(self.filename))
        # self.scenario_id_en = scenario_id if scenario_id is not None else random.randrange(0, len(self.filename_en))
        if locale == "en":
            self.scenario_id_en = scenario_id if scenario_id is not None and scenario_id < len(self.filename_en) else random.randrange(1, len(self.filename_en))
        else:
            self.scenario_id = scenario_id if scenario_id is not None and scenario_id < len(self.filename) else random.randrange(0, len(self.filename))

        self.folder =  os.path.join("onboarding", self.filename[self.scenario_id]) if locale!="en" else os.path.join("onboarding", self.filename_en[self.scenario_id_en])
        # print(self.folder)
        # self.folder =  os.path.join("onboarding", "scenario_7")
        self.scores = {
            "情绪侦查力": 0,
            "情绪掌控力": 0,
            "人际平衡术": 0,
            "沟通表达力": 0,
            "社交得体度": 0
        } if locale!="en" else{
            "Perception": 0,
            "Self Regulation": 0,
            "Empathy": 0,
            "Social Skill": 0,
            "Motivation": 0
        }
        self.choice_count = 0
        self.analysis_data = []

    def get_latest_scenario_folder(self):
        scenario_folders = [f for f in os.listdir(".") if f.startswith("scenario_")]
        if not scenario_folders:
            raise Exception("没有找到场景文件夹。请先生成对话树。")
        return max(scenario_folders)

    def load_json(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail=f"文件 {filepath} 不是有效的 JSON 格式。")
        except IOError:
            raise HTTPException(status_code=404, detail=f"无法读取文件 {filepath}。")

    def get_scene(self):
        filepath = os.path.join(self.folder, f"branch_{self.current_branch}.json")
        return all_scenario_data[filepath]

    def make_choice(self, choice: int):
        scene = self.get_scene()
        if 1 <= choice <= len(scene['scenes']['options']):
            chosen_option = scene['scenes']['options'][choice - 1]
            self.update_scores(chosen_option['scores'])
            self.choice_count += 1

            if self.choice_count == 5:
                return {"message": "Final choice made. Processing data in background."}
            
            # 记录对话历史
            self.analysis_data.append({
                "background": scene['scenes']['background'],
                "description": scene['scenes']['description'],
                "choice": chosen_option['text'],
                "analysis": chosen_option['analysis']
            })
            
            self.current_branch += str(choice)
            return self.get_scene()
        else:
            raise HTTPException(status_code=400, detail="无效的选择")
        
    def update_scores(self, new_scores: Dict[str, int]):
        for key in self.scores:
            self.scores[key] += new_scores[key]

    def process_scores(self):
        if self.choice_count == 0:
            return self.scores
        
        for key in self.scores:
            avg_score = self.scores[key] / self.choice_count
            scaled_score = min(max(round(avg_score * 4), 0), 20)
            self.scores[key] = scaled_score

        min_score = min(self.scores.values())
        min_score_idx = list(self.scores.values()).index(min_score)

        return self.scores, min_score_idx

    def get_analysis_data(self):
        return self.analysis_data
    
    async def process_final_data(self, locale: Optional[str] = None):
        scores, min_score_idx= self.process_scores()
        analysis_data = self.get_analysis_data()

        # 异步调用LLM处理函数
        if locale !="en":
            response = await process_with_llm(scores, analysis_data)
        else:
            response = await process_with_llm_en(scores, analysis_data)
        # 这里可以添加将结果保存到数据库或其他操作
        return min_score_idx, response


# 全局字典用于存储用户的 ScenarioManager 实例
user_scenarios: Dict[str, ScenarioManager] = {}

def get_scenario_manager(job_id: str, scenario_id: Optional[int] = None, locale: Optional[str] = None) -> ScenarioManager:
    if job_id not in user_scenarios:
        user_scenarios[job_id] = ScenarioManager(scenario_id, locale=locale)
    return user_scenarios[job_id]

def reset_scenario_manager(job_id: str, scenario_id: Optional[int] = None, locale: Optional[str] = None):
    user_scenarios[job_id] = ScenarioManager(scenario_id, locale=locale)

@router.post("/start_scenario/{job_id}")
async def start_scenario(job_id: str, locale: Optional[str] = None):
    reset_scenario_manager(job_id, locale=locale)
    scenario = get_scenario_manager(job_id, locale=locale)
    scenario.current_branch = ""
    scenario.scores = {key: 0 for key in scenario.scores}
    scenario.choice_count = 0
    scenario.analysis_data = []
    return {"scene": scenario.get_scene(), "scenario_id": scenario.scenario_id+1 if locale!="en" else scenario.scenario_id_en+1}

async def background_process_data(scenario_manager: ScenarioManager, job_id: str, db: Session = Depends(database.get_db), locale: Optional[str] = None):
    min_score_idx, response = await scenario_manager.process_final_data(locale)
    
    # update personal info
    tags = ["超绝顿感力", "情绪小火山", "职场隐士", "交流绝缘体", "交流绝缘体"] if locale!="en" else ["Perception", "Self Regulation", "Empathy", "Social Skill", "Motivation"]
    tag_description = ["超绝顿感力tag_description", "情绪小火山tag_description", "职场隐士tag_description", "交流绝缘体tag_description", "交流绝缘体tag_description"] if locale!="en" else ["tag_description0", "tag_description1", "tag_description2", "tag_description3", "tag_description4"]
    
    personal_info = crud.get_personal_info_by_job_id(db, job_id)
    print(f"Retrieved PersonalInfo: {personal_info.name}")
    personal_info_update = schemas.PersonalInfoUpdate(
        tag=tags[min_score_idx],
        tag_description=tag_description[min_score_idx]
    )
    updated_personal_info = crud.update_personal_info_by_name(db, personal_info.name, personal_info_update)
    print(f"Updated PersonalInfo: {updated_personal_info.tag}")
    
    # create eq score
    eq_score_data = schemas.EQScoreCreate(
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
        overall_suggestion=response["overall_suggestion"],
        job_id=job_id
    )
    eq_score = crud.create_eq_score(db, eq_score_data)
    print(f"Created EQScore: {eq_score}")

    if job_id in user_scenarios:
        del user_scenarios[job_id]
        print(f"已删除 job_id 为 {job_id} 的 ScenarioManager 实例。")


@router.post("/choose_scenario")
async def make_choice(choice: Choice, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db), locale: Optional[str] = None):
    job_id = choice.job_id
    scenario = get_scenario_manager(job_id)
    if scenario.choice_count == 4:
        scenario.make_choice(choice.choice)
        background_tasks.add_task(background_process_data, scenario, job_id, db, locale)
        return {"message": "Final choice made. Processing data in background."}
    else:
        return scenario.make_choice(choice.choice)

@router.post("/get_current_scenario/{job_id}")
async def get_current_scene(job_id: str, locale: Optional[str] = None):
    scenario = get_scenario_manager(job_id)
    return {"scene": scenario.get_scene(), "scenario_id": scenario.scenario_id+1 if locale!="en" else scenario.scenario_id_en+1}
    # return scenario_manager.get_scene()

@router.post("/start_scenario_by_scenario_id/{job_id}/{scenario_id}")  # 0-9
async def start_scenario_by_scenario_id(job_id: str, scenario_id:int):
    reset_scenario_manager(job_id, scenario_id)
    scenario = get_scenario_manager(job_id, scenario_id)
    scenario.current_branch = ""
    scenario.scores = {key: 0 for key in scenario.scores}
    scenario.choice_count = 0
    scenario.analysis_data = []
    return {"scene": scenario.get_scene(), "scenario_id": scenario.scenario_id+1}
