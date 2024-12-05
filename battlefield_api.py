import json
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from collections import defaultdict
from fastapi.concurrency import run_in_threadpool
import asyncio

import data_types
import task_lib
from database import database, crud, schemas

from llm.chat_battlefield_agent import request_LLM_response, request_LLM_response_by_eval
from text_to_voice import call_azure_tts

router = APIRouter()


# @router.get("/get_battlefield/{user_id}")
# def get_battlefield(user_id: int, locale: str, db: Session = Depends(database.get_db)):
#     eq_scores = crud.get_eq_scores_by_person_id(db, user_id=user_id)

#     if not eq_scores:
#         print("no eq scores")
#         lowest_dimension = 1
#     else:
#         scores = {
#             "dimension1": eq_scores.dimension1_score,
#             "dimension2": eq_scores.dimension2_score,
#             "dimension3": eq_scores.dimension3_score,
#             "dimension4": eq_scores.dimension4_score,
#             "dimension5": eq_scores.dimension5_score
#         }
        
#         # find the lowest dim
#         lowest_dimension_key = min(scores, key=scores.get)
#         lowest_dimension = int(lowest_dimension_key.replace("dimension", ""))
        
#     eq_dimensions = ["情绪侦查力", "情绪掌控力", "人际平衡术", "沟通表达力", "社交得体度"]
#     # eq_type = eq_dimensions[lowest_dimension]
#     eq_type = "情绪掌控力"

#     person_course = crud.get_coursesperson_by_person_id_all(db, person_id=user_id)
#     if not person_course:
#         new_course = crud.get_course_by_course_dim_and_level(db, course_dim=eq_type, course_level=1)
#         return {"courses": [new_course.id]}
#     else:
#         return {"courses": person_course}
#     # return {"course": person_course}

@router.get("/course_exists/{person_id}")
def course_exists(person_id: int, locale: str, db: Session = Depends(database.get_db)):
    record = crud.course_exists(db, person_id=person_id)
    return record

@router.post("/update/diamond")
def update_diamond(request: data_types.DiamondUpdate, locale: str, db: Session = Depends(database.get_db)):
    db_star = crud.update_personal_diamond(db, id=request.person_id, num_diamond=request.num_diamond)
    return {"diamond_num": db_star, "message": True}

@router.get("/get_course/{user_id}/{course_id}")
def get_course_status(user_id: int, course_id: int, locale: str, db: Session = Depends(database.get_db)):
    db_course = crud.get_coursesperson_by_person_id(db, person_id=user_id, course_id=course_id)
    return {"course": db_course}


@router.get("/get_battlefield_map/{person_id}")
def get_battlefield_map(
    person_id: int,
    dim_name: str,
    locale: str,
    db: Session = Depends(database.get_db)
):  
    course_list = crud.get_course_by_course_dim(db, dim_name, locale)
    course_result = crud.get_courseResults_by_person_id(db, person_id, dim_name, locale)
    print("debug course_list: ", course_list)
    print("debug course_result: ", course_result)

    next_course_id = course_list[0].id
    for i in range(len(course_result)):
        res = course_result[i]
        status = res.status
        if status == "complete":
            if i != len(course_result)-1:
                next_course_id = course_list[i+1].id
    return {"course_list": course_list, "course_result": course_result, "next_course_id": next_course_id}

@router.get("/get_course_data/{course_id}")
def get_course_by_id(course_id: int, locale: str, db: Session = Depends(database.get_db)):
    course_data = crud.get_course_data_by_id(db, course_id)
   
    return {"course_data": course_data}

@router.get("/get_course_analysis/{person_id}/{course_id}")
def get_course_analysis(person_id: int, course_id: int, locale: str, db: Session = Depends(database.get_db)):
    course_analysis = crud.get_coursesperson_by_person_id(db, person_id, course_id)

    return {"course_analysis": course_analysis}


async def add_voice_to_response(response, npc_map):
    tasks = []
    for i, npc in enumerate(response['dialog']):
        role = npc['role']
        content = npc['content']
        voice, style, rate = npc_map[role]

        tasks.append(run_in_threadpool(call_azure_tts, content, voice, style, rate))

    # in parallel
    voice_urls = await asyncio.gather(*tasks)

    # update response
    for i, npc in enumerate(response['dialog']):
        response['dialog'][i] = {
            'role': npc['role'],
            'content': npc['content'],
            'voice_url': voice_urls[i]
        }

    return response

@router.post("/chat/battlefield")
async def chat_battlefield(request: data_types.BattlefieldRequest, locale: str, db: Session = Depends(database.get_db)):
    person_id = request.person_id
    course_id = request.course_id
    locale = request.locale

    # prevcondition npc
    npcs = json.loads(request.npcs)
    npc_map = defaultdict(list)
    for i in range(3):
        npc_idx = f"npc{i+1}"
        npc = npcs[npc_idx]

        name = npc['name']
        voice = npc['voice']
        style = npc['style']
        rate = npc['rate']
        npc_map[name] = (voice, style, rate)

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
    print("original:", response)

    # add voice to response
    if "dialog" in response:
        response = await add_voice_to_response(response, npc_map)
        # for i, npc in enumerate(response['dialog']):
        #     role = npc['role']
        #     content = npc['content']
        #     voice = npc_map[role][0]
        #     style = npc_map[role][1]
        #     rate = npc_map[role][2]

        #     voice_url = call_azure_tts(content, voice, style, rate)
        #     response['dialog'][i] = {
        #         'role': role,
        #         'content': content,
        #         'voice_url': voice_url
        #     }
        # print("update:", response)


    # check task status
    task_check = 0
    if course_id == 1 or course_id == 2:
        task_check = task_lib.check_course1(response)
    elif course_id == 3 or course_id == 4:
        task_check = task_lib.check_course3(response)
    return {"response": response, "task_check": task_check}


@router.post("/eval/battlefield")
def create_course_eval(request: data_types.BattlefieldEval, locale: str, db: Session = Depends(database.get_db)):
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

    course_entry = schemas.PersonalInfoCoursesCreate(
        user_id=person_id,
        course_id=course_id,
        course_dim=course_dim,
        course_level=course_level,
        status=request.status,
        result=request.result,
        comment1=eval_data[0]['analysis'] if len(eval_data) > 0 else None,
        comment2=eval_data[1]['analysis'] if len(eval_data) > 1 else None,
        comment3=eval_data[2]['analysis'] if len(eval_data) > 2 else None,
        locale=locale
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
