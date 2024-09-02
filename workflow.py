import uuid
from fastapi import APIRouter, BackgroundTasks
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from database import database, schemas, crud, models
from llm import eq_eval
import helper

router = APIRouter()

# create a new user
@router.post("/create_personal_info")
async def create_personal_info_endpoint(name: str, tag: str, tag_description: str, job_id: str, db: Session = Depends(database.get_db)):
    personal_info_data = schemas.PersonalInfoCreate(name=name, tag=tag, tag_description=tag_description, job_id=job_id)
    db_personal_info = crud.create_personal_info(db, personal_info_data)
    return db_personal_info

# create a new eq score report
@router.post("/create_eq_scores")
async def create_eqscore_endpoint(person_id: int, scores_details:dict, job_id: str, db: Session = Depends(database.get_db)):
    eq_score_data = schemas.EQScoreCreate(
            person_id=person_id,
            dimension1_score=scores_details['dimension1_score'],
            dimension1_detail=scores_details['dimension1_detail'],
            dimension2_score=scores_details['dimension2_score'],
            dimension2_detail=scores_details['dimension2_detail'],
            dimension3_score=scores_details['dimension3_score'],
            dimension3_detail=scores_details['dimension3_detail'],
            dimension4_score=scores_details['dimension4_score'],
            dimension4_detail=scores_details['dimension4_detail'],
            dimension5_score=scores_details['dimension5_score'],
            dimension5_detail=scores_details['dimension5_detail'],
            summary=scores_details['summary'],
            detail=scores_details['detail'],
            overall_suggestion=scores_details['overall_suggestion'],
            job_id=job_id
        )
    db_eq_score = crud.create_eq_score(db, eq_score_data)
    return db_eq_score

# signup as a new user and get the EQ Score Report
@router.post("/create_profile")
async def create_profile(request: schemas.CreateUserRequest, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    # Receive all the info from frontend
    # personal info
    username = request.info.username
    # username = "Jay Park"
    
    # preference
    gender = request.preference.gender
    issues = request.preference.issues
    # gender = "男"
    # issues = ["不太擅长回复消息"]

    concerns = ", ".join(issues)

    # test answer
    answer1 = request.test.answer1
    answer2 = request.test.answer2
    answer3 = request.test.answer3
    answer4 = request.test.answer4
    # answer1 = "等待领导决定"
    # answer2 = "不理他"
    # answer3 = "那我喝吧"
    # answer4 = "帮客户清理并解释项目情况"

    # Send necessary info to llm agent and receive response from it
    # TBD: subsitute by real test answers
    user_info = "该用户是一名" + gender + "性,ta在生活中经常受到" + concerns + "的困扰" \
                + ".ta会在开会讨论遇到两个同事意见不合并且其中一个同事小王情绪很激动的时候，" + answer1 + "。" \
                + "在饭局上，老板和ta开了一些不合适的玩笑，让ta感到非常不适，ta最有可能会" + answer2 + "。" \
                + "在酒局上，重要客户说：今天ta不喝酒就是不给客户面子，ta最有可能用" + answer3 + "这句话婉拒。" \
                + "在商务饭局上，客户说着对项目情况的担忧，同事正好把酒洒在客户身上，ta最有可能会说 “" + answer4 + "”。" 
    # user_info = "该用户是一名女性，她会在开会讨论遇到两个同事意见不合并且其中一个情绪很激动的时候，冷静分析双方意见和优缺点"

    tags = ["超绝顿感力", "情绪小火山", "职场隐士", "交流绝缘体", "交流绝缘体"]
    tag_description = "TBD"
    job_id = str(uuid.uuid4())
    background_tasks.add_task(process_user_data, request, user_info, tags, tag_description, job_id, db)

    # llm_response = eq_eval.request_LLM_response(user_info)
    # eq_scores = eq_eval.retry_parse_LLMresponse(llm_response)
    # print(eq_scores)

    # # 整理数据，明确什么是tag，什么是tag description，,如何计算以及overall score是否是五项均分
    # # TBD: tag_description
    # tag_description = "TBD"
    # scores = [eq_scores['dimension1_score'], eq_scores['dimension2_score'], eq_scores['dimension3_score'], eq_scores['dimension4_score'], eq_scores['dimension5_score']]
    # # overall_score = helper.calculate_average(*scores)
    # tags = ["超绝顿感力", "情绪小火山", "职场隐士", "交流绝缘体", "交流绝缘体"]
    # tag_id = helper.min_score_index(scores)
    # job_id = str(uuid.uuid4())

    # # create a new user
    # db_personal_info = await create_personal_info_endpoint(name=username, tag=tags[tag_id], tag_description=tag_description, job_id=job_id, db=db)
    
    # # create EQ score
    # await create_eqscore_endpoint(person_id=db_personal_info.id, scores_details=eq_scores, job_id=job_id, db=db)

    return {"job_id": job_id}

async def process_user_data(request, user_info, tags, tag_description, job_id, db):
    llm_response = eq_eval.request_LLM_response(user_info)
    eq_scores = eq_eval.retry_parse_LLMresponse(llm_response)
    tag_id = helper.min_score_index([eq_scores['dimension1_score'], eq_scores['dimension2_score'], eq_scores['dimension3_score'], eq_scores['dimension4_score'], eq_scores['dimension5_score']])
    
    # create a new user and EQ score
    db_personal_info = await create_personal_info_endpoint(name=request.info.username, tag=tags[tag_id], tag_description=tag_description, job_id=job_id, db=db)
    await create_eqscore_endpoint(person_id=db_personal_info.id, scores_details=eq_scores, job_id=job_id, db=db)

@router.get("/get_profile/{job_id}")
async def get_profile(request: Request, job_id: str, db: Session = Depends(database.get_db)):
    personal_info = crud.get_personal_info_by_job_id(db, job_id)
    eq_scores = crud.get_eq_scores_by_job_id(db, job_id)

    if not personal_info:
        return {"message": "Uncomplete1"}
    if not eq_scores:
        return {"message": "Uncomplete2"}
    
    scores = [eq_scores.dimension1_score, eq_scores.dimension2_score, eq_scores.dimension3_score, eq_scores.dimension4_score, eq_scores.dimension5_score]
    overall_score = helper.calculate_average(*scores)
    
    response = {
        "personal_info": {
            "name": personal_info.name,
            "tag": personal_info.tag,
            "tag_description": personal_info.tag_description,
            "job_id": personal_info.job_id
        },
        "eq_scores": {
            "score": overall_score, 
            "dimension1_score": eq_scores.dimension1_score, "dimension1_detail": eq_scores.dimension1_detail,
            "dimension2_score": eq_scores.dimension2_score, "dimension2_detail": eq_scores.dimension2_detail,
            "dimension3_score": eq_scores.dimension3_score, "dimension3_detail": eq_scores.dimension3_detail,
            "dimension4_score": eq_scores.dimension4_score, "dimension4_detail": eq_scores.dimension4_detail,
            "dimension5_score": eq_scores.dimension5_score, "dimension5_detail": eq_scores.dimension5_detail,
            "summary": eq_scores.summary,
            "detail": eq_scores.detail,
            "overall_suggestion": eq_scores.overall_suggestion
            }
    }
    
    return response


# login to the existed user
@router.post("/login_personal_info/{name}")
def loginin_user(request: Request, name: str, db: Session = Depends(database.get_db)):
    personal_id = crud.get_personal_id_by_name(db, name=name)

    return personal_id


# if __name__ == "__main__":
#     create_user()