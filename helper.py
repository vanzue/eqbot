def calculate_average(*args):
    return sum(args) / len(args) if args else 0

def min_score_index(scores: list):
    min_score = min(scores)
    return scores.index(min_score)

if __name__ == "__main__":
    # tags = ["超绝顿感力", "情绪小火山", "职场隐士", "交流绝缘体", "交流绝缘体"]
    # id = min_score_index([1,2,3,4,5])
    # print(tags[id])
    scores = [1,2,3,4,5]
    print(calculate_average(*scores))