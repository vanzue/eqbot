from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json
import os
from typing import List, Dict

from database import crud, database, schemas
from llm.profile_eval import process_with_llm

router = APIRouter()


class Choice(BaseModel):
    choice: int
    job_id: str

class ScenarioManager:
    def __init__(self):
        self.current_branch = ""
        # self.folder = self.get_latest_scenario_folder()
        # self.folder = "onboarding\\scenario_20240912_175052"
        self.folder =  os.path.join("onboarding", "scenario_20240912_175052")
        self.scores = {
            "情绪侦查力": 0,
            "情绪掌控力": 0,
            "人际平衡术": 0,
            "沟通表达力": 0,
            "社交得体度": 0
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
        return self.load_json(filepath)

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
            scaled_score = min(max(round(avg_score * 20), 0), 100)
            self.scores[key] = scaled_score

        min_score = min(self.scores.values())
        min_score_idx = list(self.scores.values()).index(min_score)

        return self.scores, min_score_idx

    def get_analysis_data(self):
        return self.analysis_data
    
    async def process_final_data(self):
        scores, min_score_idx= self.process_scores()
        analysis_data = self.get_analysis_data()

        # 异步调用LLM处理函数
        response = await process_with_llm(scores, analysis_data)
        # 这里可以添加将结果保存到数据库或其他操作
        return min_score_idx, response

scenario_manager = ScenarioManager()

@router.post("/start_scenario")
async def start_scenario():
    print(os.getcwd())
    scenario_manager.current_branch = ""
    scenario_manager.scores = {key: 0 for key in scenario_manager.scores}
    scenario_manager.choice_count = 0
    scenario_manager.analysis_data = []
    return scenario_manager.get_scene()

async def background_process_data(scenario_manager: ScenarioManager, job_id: str, db: Session = Depends(database.get_db)):
    min_score_idx, response = await scenario_manager.process_final_data()
    
    # update personal info
    tags = ["超绝顿感力", "情绪小火山", "职场隐士", "交流绝缘体", "交流绝缘体"]
    tag_description = ["超绝顿感力tag_description", "情绪小火山tag_description", "职场隐士tag_description", "交流绝缘体tag_description", "交流绝缘体tag_description"]
    
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
        overall_suggestion=response["overall_suggestion"],
        job_id=job_id
    )
    eq_score = crud.create_eq_score(db, eq_score_data)
    print(f"Created EQScore: {eq_score}")

@router.post("/choose_scenario")
async def make_choice(choice: Choice, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    print("job_id: " + choice.job_id)
    if scenario_manager.choice_count == 4:
        scenario_manager.make_choice(choice.choice)
        background_tasks.add_task(background_process_data, scenario_manager, choice.job_id, db)
        return {"message": "Final choice made. Processing data in background."}
    else:
        return scenario_manager.make_choice(choice.choice)

@router.post("/get_current_scenario")
async def get_current_scene():
    return scenario_manager.get_scene()

@router.get("/get_scores")
async def get_scores():
    print(scenario_manager.choice_count)
    return scenario_manager.get_average_scores()

@router.get("/get_analysis_data")
async def get_analysis_data():
    return scenario_manager.get_analysis_data()

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)