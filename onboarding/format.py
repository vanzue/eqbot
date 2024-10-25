# import json

# # 示例 JSON 数据
# data = {
#     "scenes": {
#         "background": "讨论完提案的时间规划后，[小李]突然转向你。",
#         "role": "[小李]",
#         "location": "办公室",
#         "description": "你觉得提案里加入那个新功能的建议怎么样？",
#         "options": [
#             {
#                 "text": "1.我认为新功能的加入可以增加项目的竞争力，但需要考虑时间和资源的投入。",
#                 "scores": {
#                     "情绪侦查力": 4,
#                     "情绪掌控力": 3,
#                     "人际平衡术": 3,
#                     "沟通表达力": 4,
#                     "社交得体度": 3
#                 },
#                 "analysis": "你展示了对新功能的积极态度，同时也表现了对实际操作可行性的考虑，体现了较好的情绪侦查力和沟通表达力。"
#             },
#             {
#                 "text": "2.新功能听起来不错，不过我觉得可能会增加团队的负担，需要慎重考虑。",
#                 "scores": {
#                     "情绪侦查力": 3,
#                     "情绪掌控力": 4,
#                     "人际平衡术": 2,
#                     "沟通表达力": 3,
#                     "社交得体度": 2
#                 },
#                 "analysis": "你提出了对新功能可能带来的负面影响，表现了较好的情绪掌控力，但在人际平衡术和社交得体度上显得欠缺。"
#             },
#             {
#                 "text": "3.新功能是个好点子，不过具体的实现方式还需要大家一起讨论完善。",
#                 "scores": {
#                     "情绪侦查力": 3,
#                     "情绪掌控力": 2,
#                     "人际平衡术": 4,
#                     "沟通表达力": 3,
#                     "社交得体度": 4
#                 },
#                 "analysis": "你通过强调团队合作表现了较好的人际平衡术和社交得体度，但在情绪掌控力上稍显不足。"
#             }
#         ]
#     }
# }

# # 删除 [] 的函数
# def remove_brackets(text):
#     return text.replace("[", "").replace("]", "")

# # 删除编号的函数
# def remove_numbering(text):
#     return text.lstrip("1234567890.")

# # 修改 JSON 数据
# data['scenes']['background'] = remove_brackets(data['scenes']['background'])
# data['scenes']['role'] = remove_brackets(data['scenes']['role'])
# data['scenes']['description'] = remove_brackets(data['scenes']['description'])

# for option in data['scenes']['options']:
#     option['text'] = remove_numbering(option['text'])

# # 打印修改后的 JSON 数据
# print(json.dumps(data, ensure_ascii=False, indent=4))

import os
import json

# 删除 [] 的函数
def remove_brackets(text):
    return text.replace("[", "").replace("]", "")

def remove_brackets2(text):
    return text.replace("(", "").replace(")", "")

# 删除编号的函数
def remove_numbering(text):
    return text.lstrip("1234567890.")

# 处理单个文件的函数
def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print(f"无法解析 JSON 文件: {file_path}")
            return

    # 修改 JSON 数据
    if 'scenes' in data:
        data['scenes']['background'] = remove_brackets(data['scenes'].get('background', ''))
        data['scenes']['role'] = remove_brackets(data['scenes'].get('role', ''))
        data['scenes']['description'] = remove_brackets(data['scenes'].get('description', ''))

        data['scenes']['background'] = remove_brackets2(data['scenes'].get('background', ''))
        data['scenes']['role'] = remove_brackets2(data['scenes'].get('role', ''))
        data['scenes']['description'] = remove_brackets2(data['scenes'].get('description', ''))

        for option in data['scenes'].get('options', []):
            option['text'] = remove_numbering(option.get('text', ''))

    # 将修改后的数据写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"已处理文件: {file_path}")

# 遍历文件夹并处理所有文件
def process_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith('.json'):
                file_path = os.path.join(root, file_name)
                # print(file_path)
                process_file(file_path)

# process_file("D:\\VSCode_Porgrams\\eqbot\\onboarding\\scenario_1\\branch_.json")

# 设定目标文件夹路径
folder_path = r'D:\\VSCode_Porgrams\\eqbot\\onboarding\\scenario_2_en'  # 修改为你的文件夹路径

# 开始处理文件夹中的所有 JSON 文件
process_folder(folder_path)
