import json
import os
import sys

abilities = ["Emotion Perception", "Self Regulation", "Empathy", "Social Skill", "Motivation"]

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_json(filepath):
    try:
        with open(resource_path(filepath), 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"错误：文件 {filepath} 不是有效的 JSON 格式。")
        sys.exit(1)
    except IOError:
        print(f"错误：无法读取文件 {filepath}。")
        sys.exit(1)


def print_scene(scene):
    print(f"\n场景背景：{scene['scenes']['background']}")
    print(f"场景描述：{scene['scenes']['description']}")
    for i, option in enumerate(scene['scenes']['options'], 1):
        print(f"{i}. {option['text']}")
    print("0. 退出对话")


def choose_option(scene):
    while True:
        try:
            choice = int(input("\n请选择一个选项（输入选项编号，0 退出）："))
            if choice == 0:
                return -1
            if 1 <= choice <= len(scene['scenes']['options']):
                return choice - 1
            else:
                print("无效的选择，请重试。")
        except ValueError:
            print("请输入有效的数字。")


def print_current_scores(scores):
    # print("\n当前分数：")
    for ability, score in scores.items():
        print(f"{ability}: {score:.2f}")


def navigate_dialogue_tree(folder):
    current_branch = ""
    all_scores = []
    analysis_data = []

    while True:
        filepath = os.path.join(resource_path(folder), f"branch_{current_branch}.json")
        if not os.path.exists(filepath):
            break

        scene = load_json(filepath)
        print_scene(scene)
        choice = choose_option(scene)

        if choice == -1:
            print("你选择退出对话。")
            break

        selected_option = scene['scenes']['options'][choice]
        all_scores.append(selected_option['scores'])

        analysis_data.append({
            "background": scene['scenes']['background'],
            "description": scene['scenes']['description'],
            "chosen_option": selected_option['text'],
            "analysis": selected_option['analysis']
        })

        current_branch += str(choice + 1)

        print_current_scores(calculate_average_score(all_scores))

    return all_scores, analysis_data


def calculate_average_score(scores_list):
    if not scores_list:
        return {ability: 0 for ability in abilities}
    return {ability: sum(score[ability] for score in scores_list) / len(scores_list) for ability in abilities}


def start_interaction():
    print("开始 start_interaction 函数")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"_MEIPASS 路径: {getattr(sys, '_MEIPASS', 'Not found')}")

    # 获取最新的场景文件夹
    # scenario_folders = [f for f in os.listdir(resource_path(".")) if f.startswith("scenario_")]
    # if not scenario_folders:
    #     print("没有找到场景文件夹。请先生成对话树。")
    #     return

    # latest_folder = max(scenario_folders)
    # print(f"使用最新的场景文件夹: {latest_folder}")
    latest_folder = "scenario_1_en"

    all_scores, analysis_data = navigate_dialogue_tree(resource_path(latest_folder))

    if not all_scores:
        print("对话已结束，没有做出任何选择。")
        return

    average_scores = calculate_average_score(all_scores)

    print("\n所有选择中各项能力的平均分：")
    for ability, avg_score in average_scores.items():
        print(f"{ability}: {avg_score:.2f}")

    print("\n你做出的选择分析：")
    for data in analysis_data:
        print(f"\n场景背景：{data['background']}")
        print(f"场景描述：{data['description']}")
        print(f"你的选择：{data['chosen_option']}")
        print(f"分析：{data['analysis']}")

    input("按回车键退出...")


def main():
    print("程序开始执行...")
    try:
        start_interaction()
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        print("程序执行结束")
        input("按回车键退出...")


if __name__ == "__main__":
    main()

# pyinstaller --onefile --add-data="scenario_20240911_110132;scenario_20240911_110132" read_json.py