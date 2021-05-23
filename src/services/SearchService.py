import datetime
from decimal import *
from preprocess_data import Question

# 创建问题处理对象，这样模型就可以常驻内存
que = Question()


class SearchService:
    search_cache = {}

    @classmethod
    def get_search_ans(cls, question):
        result = que.question_process(question)
        return {
            'code': 0,
            'answer': result
        }


if __name__ == '__main__':
    res = que.question_process("章子怡演过多少部电影？")
    print(res)
    res = que.question_process("卧虎藏龙是什么类型的电影？")
    print(res)
