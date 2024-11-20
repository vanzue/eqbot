import uuid
import json
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

import data_types
from database import database, crud, schemas

from llm.chat_battlefield import request_LLM_response, chat_eval, request_LLM_response_v2

router = APIRouter()


# @router.post("/chat/batttlefield/v2")
# def chat_battlefield(request: data_types.BattlefieldRequest, db: Session = Depends(database.get_db)):
#     personal_id = request.person_id
#     course_id = request.course_id
    
#     matching_course = crud.get_course_by_coursid(db, course_id=course_id)
#     print(matching_course.prompt)

#     response = request_LLM_response_v2(json.loads(request.chat_content), matching_course.prompt)
#     return response

@router.post("/chat/batttlefield")
def chat_battlefield(request: data_types.BattlefieldRequest, db: Session = Depends(database.get_db)):
    personal_id = request.person_id
    course_id = request.course_id

    matching_course = crud.get_course_by_coursid(db, course_id=course_id)
    print(matching_course.prompt)

    response = request_LLM_response(json.loads(request.chat_content), matching_course.prompt)
    return response


@router.post("/eval/battlefield") 
def create_course_eval(request: data_types.BattlefieldEval, db: Session = Depends(database.get_db)):
    # return chat_eval(request.chat_content)
    eval_data = chat_eval(request.chat_content)['eval']
    course_type, course_level = crud.get_course_by_id(db, course_id=request.course_id)
    # print(course_type, course_level)

    # update stars
    person_star = request.person_star
    # db_person = crud.get_personal_id_by_personid(db, personid=request.person_id)
    # db_person.num_star += person_star
    db_star = crud.update_personal_stars(db, id=request.person_id, num_stars=person_star)
    # print("number of stars: ", db_star)

    # 创建新的数据库条目
    course_entry = schemas.PersonalInfoCoursesCreate(
        person_id=request.person_id,
        course_id=request.course_id,
        course_type=course_type,
        course_level=course_level, 
        status=request.status,
        result=request.result,
        comment1=eval_data[0]['analysis'] if len(eval_data) > 0 else None,
        comment2=eval_data[1]['analysis'] if len(eval_data) > 1 else None,
        comment3=eval_data[2]['analysis'] if len(eval_data) > 2 else None
    )
    # print(eval_data[0]['analysis'] if len(eval_data) > 0 else None)
    # print(eval_data[1]['analysis'] if len(eval_data) > 1 else None)
    # print(eval_data[2]['analysis'] if len(eval_data) > 2 else None)

    # create new
    db_course = crud.get_coursesperson_by_person_id(db, request.person_id, request.course_id)
    # print(db_course.person_id, db_course.course_id)
    if db_course is None:
        print("not have")
        db_course = crud.create_personal_info_course(db, course_entry)
    else:
        print("have")
        db_course = crud.update_personal_info_course(db, 
                                                    person_id=request.person_id,
                                                    course_id=request.course_id,
                                                    course_level=course_level,
                                                    status=request.status,
                                                    result=request.result,
                                                    comment1=eval_data[0]['analysis'] if len(eval_data) > 0 else None,
                                                    comment2=eval_data[1]['analysis'] if len(eval_data) > 1 else None,
                                                    comment3=eval_data[2]['analysis'] if len(eval_data) > 2 else None)
    return {"db_course": db_course}



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

    person_course = crud.get_coursesperson_by_person_id_all(db, user_id=user_id)
    if not person_course:
        new_course = crud.get_course_by_course_type_and_level(db, course_type=eq_type, course_level=1)
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
    course_list = [
        {
            "id": 1,
            "course_dim": "Emotional Intelligence",
            "course_level": 1,
            "prompt": "Learn how to manage emotions effectively in challenging situations.",
            "title": "Mastering Emotional Resilience",
            "npc": [
                {"name": "John", "role": "mentor", "mood": "happy"},
                {"name": "Sarah", "role": "challenger", "mood": "neutral"}
            ],
            "image": b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff"
        },  
        {
            "id": 2,
            "course_dim": "Emotional Intelligence",
            "course_level": 2,
            "prompt": "Learn how to manage emotions effectively in challenging situations.",
            "title": "Mastering Emotional Resilience",
            "npc": [
                {"name": "John", "role": "mentor", "mood": "happy"},
                {"name": "Sarah", "role": "challenger", "mood": "neutral"}
            ],
            "image": b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff"
        },
        {
            "id": 3,
            "course_dim": "Emotional Intelligence",
            "course_level": 3,
            "prompt": "Learn how to manage emotions effectively in challenging situations.",
            "title": "Mastering Emotional Resilience",
            "npc": [
                {"name": "John", "role": "mentor", "mood": "happy"},
                {"name": "Sarah", "role": "challenger", "mood": "neutral"}
            ],
            "image": b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff"
        }
    ]

    course_result = [
        {
            "id": 1,  # 自增的主键 ID
            "user_id": 101,  # 关联的用户 ID
            "course_id": 1,  # 关联的课程 ID
            "course_type": "Emotional Intelligence",  # 课程类型
            "course_level": 1,  # 课程等级
            "status": "complete",  # 当前状态（如：completed、in-progress、not-started）
            "result": 3,  # 结果：星级评分（1-3）
            "comment1": "The course content was very insightful.",  # 第一条评论
            "comment2": "The NPC interactions made it engaging.",  # 第二条评论
            "comment3": "I would recommend this to others.",  # 第三条评论
        },
        {
            "id": 2,
            "user_id": 101, 
            "course_id": 201, 
            "course_type": "Emotional Intelligence", 
            "course_level": 2, 
            "status": "incomplete", 
            "result": 0,
            "comment1": "",
            "comment2": "",  
            "comment3": "",  
        }
    ]


    return {"course_list": course_list, "course_result": course_result, "next_course_id": 3}

@router.get("/get_course_data/{course_id}")
def get_course_by_id(course_id: int, db: Session = Depends(database.get_db)):
    course_data = {
            "id": 1,
            "course_dim": "Emotional Intelligence",
            "course_level": 1,
            "prompt": "Learn how to manage emotions effectively in challenging situations.",
            "title": "Mastering Emotional Resilience",
            "npc": [
                {"name": "John", "role": "mentor", "mood": "happy"},
                {"name": "Sarah", "role": "challenger", "mood": "neutral"}
            ],
            "image": b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff"
        }
    
    return {"course_data": course_data}

@router.get("/get_course_analysis/{person_id}/{course_id}")
def get_course_analysis(person_id: int, course_id: int, db: Session = Depends(database.get_db)):
    course_analysis = {
        "id": 1,  # 自增的主键 ID
        "user_id": 101,  # 关联的用户 ID
        "course_id": 1,  # 关联的课程 ID
        "course_type": "Emotional Intelligence",  # 课程类型
        "course_level": 1,  # 课程等级
        "status": "complete",  # 当前状态（如：completed、in-progress、not-started）
        "result": 3,  # 结果：星级评分（1-3）
        "comment1": "The course content was very insightful.",  # 第一条评论
        "comment2": "The NPC interactions made it engaging.",  # 第二条评论
        "comment3": "I would recommend this to others.",  # 第三条评论
    }

    return {"course_analysis": course_analysis}


@router.post("/chat/battlefield")
def chat_battlefield(request: data_types.BattlefieldRequest, db: Session = Depends(database.get_db)):
    # person_id = request.person_id
    # course_id = request.course_id
    # lang_type = request.lang_type
    # lang_type = 'zh' if course_id == 1 else 'en'
    # matching_course = crud.get_course_by_coursid(db, course_id=course_id)
    # # print(matching_course.prompt)

    # response = request_LLM_response(json.loads(
    #     request.chat_content), matching_course.prompt, lang=lang_type)
    # return response
    return {"response": "For testing chat battlefield"}

@router.post("/eval/battlefield")
def create_course_eval(request: data_types.BattlefieldEval, db: Session = Depends(database.get_db)):
    response = {
        "id": 1,  # 自增的主键 ID
        "user_id": 101,  # 关联的用户 ID
        "course_id": 1,  # 关联的课程 ID
        "course_type": "Emotional Intelligence",  # 课程类型
        "course_level": 1,  # 课程等级
        "status": "complete",  # 当前状态（如：completed、in-progress、not-started）
        "result": 3,  # 结果：星级评分（1-3）
        "comment1": "The course content was very insightful.",  # 第一条评论
        "comment2": "The NPC interactions made it engaging.",  # 第二条评论
        "comment3": "I would recommend this to others.",  # 第三条评论
    }

    return {"response": response}