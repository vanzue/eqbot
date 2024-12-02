# if course_id = 1
# return 0: not meet requirement
# return 1: task1 finish 心情都好
# return 2: task2 finish 说出固定的话
# return 3: task1 and task2 finish
def check_course1(response):
    result = 0
    if "dialog" in response:    
        dialog = response["dialog"]
        for pr in dialog:
            if pr["role"] == "领导" and "你点的菜真不错" in pr["content"]:
                result += 2
    
    if "moods" in response:
        moods = response["moods"]
        isAllGood = True
        for pr in moods:
            mood = int(pr["mood"])
            if mood <= 0:
                isAllGood = False
        if isAllGood:
            result += 1
    
    return result

# if course = 3
# return 1: task1 finish
# return 2: task2 finish
# return 0: none of them finish
def check_course3(response):
    # task1
    isSam = True
    isJason = True
    if "eval" in response:
        eval = response["eval"]
        for pr in eval:
            role = pr['role']
            satisfaction = pr['satisfaction']
            if role == "Sam" and satisfaction!="Satisfied":
                isSam = False
            if role == "Jason" and satisfaction!="Satisfied":
                isJason = False
    if isSam and isJason:
        return 1

    # task2
    if "dialog" in response:    
        dialog = response["dialog"]
        for pr in dialog:
            # hard to pass, change "I agree with you" to "I agree"
            if "I agree" in pr['content']:
                return 2
            
    return 0