import uuid
import json
import base64
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

import data_types
import task_lib
from database import database, crud, schemas

from llm.chat_battlefield_agent import request_LLM_response, request_LLM_response_by_eval

router = APIRouter()

def encode_image_to_base64(binary_data: bytes) -> str:
    return base64.b64encode(binary_data).decode("utf-8")


# @router.post("/chat/batttlefield/v2")
# def chat_battlefield(request: data_types.BattlefieldRequest, db: Session = Depends(database.get_db)):
#     personal_id = request.person_id
#     course_id = request.course_id
    
#     matching_course = crud.get_course_by_coursid(db, course_id=course_id)
#     print(matching_course.prompt)

#     response = request_LLM_response_v2(json.loads(request.chat_content), matching_course.prompt)
#     return response

# @router.post("/chat/batttlefield")
# def chat_battlefield(request: data_types.BattlefieldRequest, db: Session = Depends(database.get_db)):
#     personal_id = request.person_id
#     course_id = request.course_id

#     matching_course = crud.get_course_by_coursid(db, course_id=course_id)
#     print(matching_course.prompt)

#     response = request_LLM_response(json.loads(request.chat_content), matching_course.prompt)
#     return response


# @router.post("/eval/battlefield") 
# def create_course_eval(request: data_types.BattlefieldEval, db: Session = Depends(database.get_db)):
#     # return chat_eval(request.chat_content)
#     eval_data = chat_eval(request.chat_content)['eval']
#     course_type, course_level = crud.get_course_by_id(db, course_id=request.course_id)
#     # print(course_type, course_level)

#     # update stars
#     person_star = request.person_star
#     # db_person = crud.get_personal_id_by_personid(db, personid=request.person_id)
#     # db_person.num_star += person_star
#     db_star = crud.update_personal_stars(db, id=request.person_id, num_stars=person_star)
#     # print("number of stars: ", db_star)

#     # 创建新的数据库条目
#     course_entry = schemas.PersonalInfoCoursesCreate(
#         person_id=request.person_id,
#         course_id=request.course_id,
#         course_type=course_type,
#         course_level=course_level, 
#         status=request.status,
#         result=request.result,
#         comment1=eval_data[0]['analysis'] if len(eval_data) > 0 else None,
#         comment2=eval_data[1]['analysis'] if len(eval_data) > 1 else None,
#         comment3=eval_data[2]['analysis'] if len(eval_data) > 2 else None
#     )
#     # print(eval_data[0]['analysis'] if len(eval_data) > 0 else None)
#     # print(eval_data[1]['analysis'] if len(eval_data) > 1 else None)
#     # print(eval_data[2]['analysis'] if len(eval_data) > 2 else None)

#     # create new
#     db_course = crud.get_coursesperson_by_person_id(db, request.person_id, request.course_id)
#     # print(db_course.person_id, db_course.course_id)
#     if db_course is None:
#         print("not have")
#         db_course = crud.create_personal_info_course(db, course_entry)
#     else:
#         print("have")
#         db_course = crud.update_personal_info_course(db, 
#                                                     person_id=request.person_id,
#                                                     course_id=request.course_id,
#                                                     course_level=course_level,
#                                                     status=request.status,
#                                                     result=request.result,
#                                                     comment1=eval_data[0]['analysis'] if len(eval_data) > 0 else None,
#                                                     comment2=eval_data[1]['analysis'] if len(eval_data) > 1 else None,
#                                                     comment3=eval_data[2]['analysis'] if len(eval_data) > 2 else None)
#     return {"db_course": db_course}



@router.get("/get_battlefield/{user_id}")
def get_battlefield(user_id: int, db: Session = Depends(database.get_db)):
    eq_scores = crud.get_eq_scores_by_person_id(db, user_id=user_id)

    if not eq_scores:
        print("no eq scores")
        lowest_dimension = 1
    else:
        scores = {
            "dimension1": eq_scores.dimension1_score,
            "dimension2": eq_scores.dimension2_score,
            "dimension3": eq_scores.dimension3_score,
            "dimension4": eq_scores.dimension4_score,
            "dimension5": eq_scores.dimension5_score
        }
        
        # 找到最低分的维度
        lowest_dimension_key = min(scores, key=scores.get)
        lowest_dimension = int(lowest_dimension_key.replace("dimension", ""))
        
    eq_dimensions = ["情绪侦查力", "情绪掌控力", "人际平衡术", "沟通表达力", "社交得体度"]
    # eq_type = eq_dimensions[lowest_dimension]
    eq_type = "情绪掌控力"

    person_course = crud.get_coursesperson_by_person_id_all(db, person_id=user_id)
    if not person_course:
        new_course = crud.get_course_by_course_dim_and_level(db, course_dim=eq_type, course_level=1)
        return {"courses": [new_course.id]}
    else:
        return {"courses": person_course}
    # return {"course": person_course}

@router.get("/course_exists/{person_id}")
def course_exists(person_id: int, db: Session = Depends(database.get_db)):
    record = crud.course_exists(db, person_id=person_id)
    return record

@router.post("/update/diamond")
def update_diamond(request: data_types.DiamondUpdate, db: Session = Depends(database.get_db)):
    db_star = crud.update_personal_stars(db, id=request.person_id, num_stars=request.num_diamond)
    return {"diamond_num": db_star, "message": True}

@router.get("/get_course/{user_id}/{course_id}")
def get_course_status(user_id: int, course_id: int, db: Session = Depends(database.get_db)):
    db_course = crud.get_coursesperson_by_person_id(db, person_id=user_id, course_id=course_id)
    return {"course": db_course}


@router.get("/get_battlefield_map/{person_id}")
def get_battlefield_map(
    person_id: int,
    dim_name: Optional[str] = None,
    db: Session = Depends(database.get_db)
):  
    course_list = crud.get_course_by_course_dim(db, dim_name)
    course_result = crud.get_courseResults_by_person_id(db, person_id, dim_name)
    # course_list = [
    #     {
    #         "id": 1,
    #         "course_dim": "Emotional Intelligence",
    #         "course_level": 1,
    #         "prompt": "Learn how to manage emotions effectively in challenging situations.",
    #         "title": "Mastering Emotional Resilience",
    #         "npc": [
    #             {"name": "John", "role": "mentor", "mood": "happy"},
    #             {"name": "Sarah", "role": "challenger", "mood": "neutral"}
    #         ],
    #         "image": None
    #     },  
    #     {
    #         "id": 2,
    #         "course_dim": "Emotional Intelligence",
    #         "course_level": 2,
    #         "prompt": "Learn how to manage emotions effectively in challenging situations.",
    #         "title": "Mastering Emotional Resilience",
    #         "npc": [
    #             {"name": "John", "role": "mentor", "mood": "happy"},
    #             {"name": "Sarah", "role": "challenger", "mood": "neutral"}
    #         ],
    #         "image": None
    #     },
    #     {
    #         "id": 3,
    #         "course_dim": "Emotional Intelligence",
    #         "course_level": 3,
    #         "prompt": "Learn how to manage emotions effectively in challenging situations.",
    #         "title": "Mastering Emotional Resilience",
    #         "npc": [
    #             {"name": "John", "role": "mentor", "mood": "happy"},
    #             {"name": "Sarah", "role": "challenger", "mood": "neutral"}
    #         ],
    #         "image": None
    #     }
    # ]

    # course_result = [
    #     {
    #         "id": 1,  # 自增的主键 ID
    #         "user_id": 101,  # 关联的用户 ID
    #         "course_id": 1,  # 关联的课程 ID
    #         "course_type": "Emotional Intelligence",  # 课程类型
    #         "course_level": 1,  # 课程等级
    #         "status": "complete",  # 当前状态（如：completed、in-progress、not-started）
    #         "result": 3,  # 结果：星级评分（1-3）
    #         "comment1": "The course content was very insightful.",  # 第一条评论
    #         "comment2": "The NPC interactions made it engaging.",  # 第二条评论
    #         "comment3": "I would recommend this to others.",  # 第三条评论
    #     },
    #     {
    #         "id": 2,
    #         "user_id": 101, 
    #         "course_id": 201, 
    #         "course_type": "Emotional Intelligence", 
    #         "course_level": 2, 
    #         "status": "incomplete", 
    #         "result": 0,
    #         "comment1": "",
    #         "comment2": "",  
    #         "comment3": "",  
    #     }
    # ]


    return {"course_list": course_list, "course_result": course_result, "next_course_id": 3}

@router.get("/get_course_data/{course_id}")
def get_course_by_id(course_id: int, db: Session = Depends(database.get_db)):
    course_data = crud.get_course_data_by_id(db, course_id)
    # course_data = {
    #         "id": 1,
    #         "course_dim": "Emotional Intelligence",
    #         "course_level": 1,
    #         "prompt": "Learn how to manage emotions effectively in challenging situations.",
    #         "title": "Mastering Emotional Resilience",
    #         "npc": [
    #             {"name": "John", "role": "mentor", "mood": "happy"},
    #             {"name": "Sarah", "role": "challenger", "mood": "neutral"}
    #         ],
    #         "image": None
    #     }
    
    return {"course_data": course_data}

@router.get("/get_course_analysis/{person_id}/{course_id}")
def get_course_analysis(person_id: int, course_id: int, db: Session = Depends(database.get_db)):
    course_analysis = crud.get_coursesperson_by_person_id(db, person_id, course_id)
    # course_analysis = {
    #     "id": 1,  # 自增的主键 ID
    #     "user_id": 101,  # 关联的用户 ID
    #     "course_id": 1,  # 关联的课程 ID
    #     "course_type": "Emotional Intelligence",  # 课程类型
    #     "course_level": 1,  # 课程等级
    #     "status": "complete",  # 当前状态（如：completed、in-progress、not-started）
    #     "result": 3,  # 结果：星级评分（1-3）
    #     "comment1": "The course content was very insightful.",  # 第一条评论
    #     "comment2": "The NPC interactions made it engaging.",  # 第二条评论
    #     "comment3": "I would recommend this to others.",  # 第三条评论
    # }

    return {"course_analysis": course_analysis}


@router.post("/chat/battlefield")
def chat_battlefield(request: data_types.BattlefieldRequest, db: Session = Depends(database.get_db)):
    person_id = request.person_id
    course_id = request.course_id
    locale = request.locale

    matching_course = crud.get_course_by_coursid(db, course_id=course_id)
    background = matching_course.prompt

    # npc post condition
    npc_str = matching_course.npc
    npc_json = json.loads(npc_str)
    result = [f"{npc['name']}: {npc['personality']}" for npc in npc_json.values()]
    final_string = "\n".join(result)

    prompt = background + final_string

    response = request_LLM_response(json.loads(
        request.chat_content), prompt, lang=locale)
    print(response)
    if course_id == 1:
        task_check = task_lib.check_course1(response)
    return {"response": response, "task_check": task_check}

@router.post("/eval/battlefield")
def create_course_eval(request: data_types.BattlefieldEval, db: Session = Depends(database.get_db)):
    # response = {
    #     "id": 1,  # 自增的主键 ID
    #     "user_id": 101,  # 关联的用户 ID
    #     "course_id": 1,  # 关联的课程 ID
    #     "course_type": "Emotional Intelligence",  # 课程类型
    #     "course_level": 1,  # 课程等级
    #     "status": "complete",  # 当前状态（如：complete、incomplete）
    #     "result": 3,  # 结果：星级评分（1-3）
    #     "comment1": "The course content was very insightful.",  # 第一条评论
    #     "comment2": "The NPC interactions made it engaging.",  # 第二条评论
    #     "comment3": "I would recommend this to others.",  # 第三条评论
    # }
    locale = request.locale
    course_id = request.course_id
    person_id = request.person_id

    eval_result = request_LLM_response_by_eval(request.chat_content, lang=locale)
    eval_data = eval_result['eval']
    tips = eval_result['eq_tips']
    course_dim, course_level = crud.get_course_by_id(db, course_id=request.course_id)

    # update stars
    person_diamond = request.person_diamond
    db_diamond = crud.update_personal_diamond(db, id=request.person_id, num_diamond=person_diamond)
    # print("number of diamonds: ", db_diamond)

    # 创建新的数据库条目
    course_entry = schemas.PersonalInfoCoursesCreate(
        user_id=person_id,
        course_id=course_id,
        course_dim=course_dim,
        course_level=course_level,
        status=request.status,
        result=request.result,
        comment1=eval_data[0]['analysis'] if len(eval_data) > 0 else None,
        comment2=eval_data[1]['analysis'] if len(eval_data) > 1 else None,
        comment3=eval_data[2]['analysis'] if len(eval_data) > 2 else None
    )

    # create new data for CoursePerson
    db_course = crud.get_coursesperson_by_person_id(
        db, request.person_id, request.course_id)
    # print(db_course.person_id, db_course.course_id)
    if db_course is None:
        db_course = crud.create_personal_info_course(db, course_entry)
    else:
        db_course = crud.update_personal_info_course(db,
                                                     person_id=request.person_id,
                                                     course_id=request.course_id,
                                                     course_level=course_level,
                                                     status=request.status,
                                                     result=request.result,
                                                     comment1=eval_data[0]['analysis'] if len(
                                                         eval_data) > 0 else None,
                                                     comment2=eval_data[1]['analysis'] if len(
                                                         eval_data) > 1 else None,
                                                     comment3=eval_data[2]['analysis'] if len(eval_data) > 2 else None)

    response = {**vars(db_course), "tips": tips}

    return {"response": response}
