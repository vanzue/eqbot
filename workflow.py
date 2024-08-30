from fastapi import APIRouter
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from eq_master_api import router as eqmaster_router
from database import get_db,  models, schemas, crud
from llm import request_LLM_response, retry_parse_LLMresponse
import helper

router = APIRouter()

# create a new user
@router.post("/creat_personal_info")
def create_personal_info_endpoint(name: str, tag: str, tag_description: str, db: Session = Depends(get_db)):
    personal_info_data = schemas.PersonalInfoCreate(name=name, tag=tag, tag_description=tag_description)
    db_personal_info = crud.create_personal_info(db, personal_info_data)
    return db_personal_info

# create a new eq score report
@router.post("/create_eq_scores")
def create_eqscore_endpoint(person_id: int, scores_details:dict, db: Session = Depends(get_db)):
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
            overall_suggestion=scores_details['overall_suggestion']
        )
    db_eq_score = crud.create_eq_score(db, eq_score_data)
    return db_eq_score

# signup as a new user and get the EQ Score Report
@router.post("/create_profile")
def create_user(request: Request):
    # Receive all the info from frontend
    # personal info
    # username = request.info.username
    username = "Jay Park"
    
    # preference
    # gender = request.preference.gender
    # issues = request.preference.issues
    gender = "男"
    issues = ["不太擅长回复消息"]

    concerns = ""
    for issue in issues:
        concerns += issue + ', '

    # test answer
    # answer1 = request.test.answer1
    # answer2 = request.test.answer2
    # answer3 = request.test.answer3
    # answer4 = request.test.answer4
    answer1 = "等待领导决定"
    answer2 = "不理他"
    answer3 = "那我喝吧"
    answer4 = "帮客户清理并解释项目情况"

    # Send necessary info to llm agent and receive response from it
    # TBD: subsitute by real test answers
    user_info = "该用户是一名" + gender + ",ta在生活中经常受到" + concerns + "的困扰" \
                + ".ta会在开会讨论遇到两个同事意见不合并且其中一个情绪很激动的时候，" + answer1 + "。" \
                + "在饭局上，老板和ta开了一些不合适的玩笑，让ta感到非常不适，ta最有可能会" + answer2 + "。" \
                + "在酒局上，重要客户说：今天ta不喝酒就是不给客户面子，ta最有可能用" + answer3 + "这句话婉拒。" \
                + "在商务饭局上，客户说着对项目情况的担忧，同事正好把酒洒在客户身上，ta最有可能会说 “" + answer4 + "”。" 
    # user_info = "该用户是一名女性，她会在开会讨论遇到两个同事意见不合并且其中一个情绪很激动的时候，冷静分析双方意见和优缺点"
    llm_response = request_LLM_response(user_info)
    eq_scores = retry_parse_LLMresponse(llm_response)

    # 整理数据，明确什么是tag，什么是tag description，,如何计算以及overall score是否是五项均分
    # TBD: tag_description
    tag_description = "TBD"
    scores = [eq_scores['dimension1_score'], eq_scores['dimension2_score'], eq_scores['dimension3_score'], eq_scores['dimension4_score'], eq_scores['dimension5_score']]
    overall_score = helper.calculate_average(*scores)
    tags = ["超绝顿感力", "情绪小火山", "职场隐士", "交流绝缘体", "交流绝缘体"]
    tag_id = helper.min_score_index(scores)

    # create a new user
    db_personal_info = create_personal_info_endpoint(name=username, tag=tags[tag_id], tag_description=tag_description)
    
    # create EQ score
    create_eqscore_endpoint(person_id=db_personal_info.id, scores_details=eq_scores)

    # return info back to frontend
    return {"score": overall_score, 
            "tag": tags[tag_id], "tag_description": tag_description,
            "dimension1_score": eq_scores['dimension1_score'], "dimension1_detail": eq_scores['dimension1_detail'],
            "dimension2_score": eq_scores['dimension2_score'], "dimension2_detail": eq_scores['dimension2_detail'],
            "dimension3_score": eq_scores['dimension3_score'], "dimension3_detail": eq_scores['dimension3_detail'],
            "dimension4_score": eq_scores['dimension4_score'], "dimension4_detail": eq_scores['dimension4_detail'],
            "dimension5_score": eq_scores['dimension5_score'], "dimension5_detail": eq_scores['dimension5_detail'],
            "summary": eq_scores['summary'],
            "detail": eq_scores['detail'],
            "overall_suggestion": eq_scores['overall_suggestion']}


# login to the existed user
@router.post("/login_personal_info/{name}")
def loginin_user(request: Request, name: str, db: Session = Depends(get_db)):
    personal_id = crud.get_personal_id_by_name(db, name=name)

    # TBD: confirm what to return
    pass

if __name__ == "__main__":
    create_user()