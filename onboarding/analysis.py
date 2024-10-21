import json
import os
import sys
import matplotlib.pyplot as plt
import matplotlib

# 设置支持中文的字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号


# abilities = ["情绪侦查力", "情绪掌控力", "人际平衡术", "沟通表达力", "社交得体度"]
abilities = ["Emotion Perception", "Self Regulation", "Empathy", "Social Skill", "Motivation"]

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
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


def calculate_average_score(scores_list):
    if not scores_list:
        return {ability: 0 for ability in abilities}
    average_scores = {ability: sum(score[ability] for score in scores_list) / len(scores_list) for ability in abilities}
    average_scores['平均分'] = sum(average_scores.values()) / len(abilities)
    return average_scores


def traverse_tree(folder, current_branch="", current_scores=None, all_paths=None):
    if current_scores is None:
        current_scores = []
    if all_paths is None:
        all_paths = []

    filepath = os.path.join(resource_path(folder), f"branch_{current_branch}.json")
    if not os.path.exists(filepath):
        return all_paths

    scene = load_json(filepath)

    for choice_index, option in enumerate(scene['scenes']['options']):
        # 记录分数
        new_scores = current_scores + [option['scores']]
        
        # 更新分支路径
        new_branch = current_branch + str(choice_index + 1)

        # 检查是否还有子场景
        next_filepath = os.path.join(resource_path(folder), f"branch_{new_branch}.json")
        if os.path.exists(next_filepath):
            # 递归遍历子场景
            traverse_tree(folder, new_branch, new_scores, all_paths)
        else:
            # 如果没有子场景了，计算平均分并记录路径
            average_scores = calculate_average_score(new_scores)
            all_paths.append({
                "branch": new_branch,
                "scores": average_scores
            })

    return all_paths


def write_scores_to_file(all_paths, output_file="output_scores.txt"):
    with open(output_file, 'w', encoding='utf-8') as f:
        for path_data in all_paths:
            f.write(f"分支路径: {path_data['branch']}\n")
            f.write("平均分：\n")
            for ability, score in path_data['scores'].items():
                f.write(f"{ability}: {score:.2f}\n")
            f.write("\n")


def plot_scores_distribution(all_paths, output_folder):
    # 初始化存储每个维度的得分列表
    scores_data = {ability: [] for ability in abilities}
    scores_data['平均分'] = []

    # 收集所有路径的分数数据
    for path_data in all_paths:
        for ability in abilities:
            scores_data[ability].append(path_data['scores'][ability])
        scores_data['平均分'].append(path_data['scores']['平均分'])

    fig, axs = plt.subplots(2, 3, figsize=(15, 10))

    # 创建每个维度和平均分的分布图
    for i, ability in enumerate(abilities + ['平均分']):
        row, col = divmod(i, 3)  # 计算子图的位置
        axs[row, col].hist(scores_data[ability], bins=10, alpha=0.7, color='blue')
        axs[row, col].set_title(f"{ability} 分数分布")
        axs[row, col].set_xlabel("得分")
        axs[row, col].set_ylabel("频率")
        axs[row, col].grid(True)

    plt.tight_layout()
    output_path = os.path.join(output_folder, "all_distributions.png")
    plt.savefig(output_path)  # 保存到场景文件夹
    plt.show()

    # # 生成六个分布图
    # for ability in abilities + ['平均分']:
    #     plt.figure()
    #     plt.hist(scores_data[ability], bins=10, alpha=0.7, color='blue')
    #     plt.title(f"{ability} 分数分布")
    #     plt.xlabel("得分")
    #     plt.ylabel("频率")
    #     plt.grid(True)
        # output_path = os.path.join(output_folder, f"{ability}_distribution.png")
        # plt.savefig(output_path) 
        # plt.show()


def start_interaction():
    print("开始遍历对话树...")
    
    # 设置场景文件夹
    # latest_folder = "scenario_20240929_104637"
    # latest_folder = "scenario_20240929_100105"
    latest_folder = "scenario_4_en"

    # 遍历所有分支并记录所有路径的得分
    all_paths = traverse_tree(latest_folder)

    if not all_paths:
        print("对话树遍历结束，没有记录到任何路径。")
        return

    # 写入得分到文件
    write_scores_to_file(all_paths)

    # 生成分布图
    plot_scores_distribution(all_paths, resource_path(latest_folder))

    print("所有路径的分数已记录在 'output_scores.txt' 文件中，分布图已生成。")


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
