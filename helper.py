def calculate_average(*args):
    return sum(args) / len(args) if args else 0

def min_score_index(scores: list):
    min_score = min(scores)
    return scores.index(min_score)

if __name__ == "__main__":
    # tags = ["超绝顿感力", "情绪小火山", "职场隐士", "交流绝缘体", "交流绝缘体"]
    # id = min_score_index([1,2,3,4,5])
    # print(tags[id])
    # scores = [1,2,3,4,5]
    # print(calculate_average(*scores))
    answer1 = "等待领导决定"
    answer2 = "不理他"
    answer3 = "那我喝吧"
    answer4 = "帮客户清理并解释项目情况"
    user_info = "该用户是一名" + gender + "性,ta在生活中经常受到" + concerns + "的困扰" \
                + ".ta会在开会讨论遇到两个同事意见不合并且其中一个情绪很激动的时候，" + answer1 + "。" \
                + "在饭局上，老板和ta开了一些不合适的玩笑，让ta感到非常不适，ta最有可能会" + answer2 + "。" \
                + "在酒局上，重要客户说：今天ta不喝酒就是不给客户面子，ta最有可能用" + answer3 + "这句话婉拒。" \
                + "在商务饭局上，客户说着对项目情况的担忧，同事正好把酒洒在客户身上，ta最有可能会说 “" + answer4 + "”。" 
    print(user_info)