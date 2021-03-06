import datetime
from decimal import *
from preprocess_data import Question

# 创建问题处理对象，这样模型就可以常驻内存
que = Question()


class SearchService:
    search_cache = {}

    @classmethod
    def get_chat_ans(cls, question,roleId):
        result = que.question_process(question,roleId,0)
        return {
            'code': 0,
            'answer': result
        }

    @classmethod
    def get_search_ans(cls, question):
        return que.question_process(question,"0",1)
    #0仅用做占位
