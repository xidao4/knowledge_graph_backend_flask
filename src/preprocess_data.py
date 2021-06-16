"""
接收原始问题
对原始问题进行分词、词性标注等处理
对问题进行抽象
"""

import os
import re
import sys
import jieba.posseg

from question_classification import Question_classify
from question_template import QuestionTemplate
from settings import *


# # 将自定义字典写入文件
# result = []
# with(open("./data/userdict.txt","r",encoding="utf-8")) as fr:
#     vocablist=fr.readlines()
#     for one in vocablist:
#         if str(one).strip()!="":
#             temp=str(one).strip()+" "+str(15)+" nr"+"\n"
#             result.append(temp)
# with(open("./data/userdict2.txt","w",encoding="utf-8")) as fw:
#     for one in result:
#         fw.write(one)

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')


# Restore
def enablePrint():
    sys.stdout = sys.__stdout__


# blockPrint()

# enablePrint()


class Question():
    def __init__(self):
        # 初始化相关设置：读取词汇表，训练分类器，连接数据库
        self.init_config()

    def init_config(self):
        # # 读取词汇表
        # with(open("./data/vocabulary.txt","r",encoding="utf-8")) as fr:
        #     vocab_list=fr.readlines()
        # vocab_dict={}
        # vocablist=[]
        # for one in vocab_list:
        #     word_id,word=str(one).strip().split(":")
        #     vocab_dict[str(word).strip()]=int(word_id)
        #     vocablist.append(str(word).strip())
        # # print(vocab_dict)
        # self.vocab=vocab_dict

        # 训练分类器
        self.classify_model = Question_classify()
        # 读取问题模板
        with(open(CLASSIFICATION_PATH, "r", encoding="utf-8")) as f:
            question_mode_list = f.readlines()
        self.question_mode_dict = {}
        for one_mode in question_mode_list:
            # 读取一行
            mode_id, mode_str = str(one_mode).strip().split(":")
            # 处理一行，并存入
            self.question_mode_dict[int(mode_id)] = str(mode_str).strip()
        # 创建问题模板对象
        self.questiontemplate = QuestionTemplate()

    def question_process(self, question,idx):
        # 接收问题
        self.raw_question = str(question).strip()
        # 对问题进行词性标注
        self.pos_quesiton = self.question_posseg()
        print('pos_question',self.pos_quesiton)
        # 得到问题的模板
        self.question_template_id_str = self.get_question_template()
        print('question_template_id_str',self.question_template_id_str)
        # 查询图数据库,得到答案
        self.answer = self.query_template(idx)
        return (self.answer)

    def question_posseg(self):
        jieba.load_userdict(USER_DICT_PATH)
        clean_question = re.sub(CLEAN_REGEX, "", self.raw_question)
        self.clean_question = clean_question
        question_seged = jieba.posseg.cut(str(clean_question))
        print("question_seged",question_seged)
        result = []
        question_word, question_flag = [], []
        for w in question_seged:
            temp_word = f"{w.word}/{w.flag}"
            result.append(temp_word)
            # 预处理问题
            word, flag = w.word, w.flag
            question_word.append(str(word).strip())
            question_flag.append(str(flag).strip())
        assert len(question_flag) == len(question_word)
        self.question_word = question_word
        self.question_flag = question_flag
        print('question_word',question_word)
        print('question_flag',question_flag)
        return result


    def get_question_template(self):
        # 抽象问题
        for item in ['nr','ns','ne','nt']:
            while item in self.question_flag:
                ix = self.question_flag.index(item)
                self.question_word[ix] = item
                self.question_flag[ix] = item + "ed"
        # 将问题转化字符串
        str_question = "".join(self.question_word)
        print("抽象问题为：", str_question)
        # 通过分类器获取问题模板编号
        question_template_num = self.classify_model.predict(str_question)
        print("使用模板编号：", question_template_num)
        question_template = self.question_mode_dict[question_template_num]
        print("问题模板：", question_template)
        question_template_id_str = str(question_template_num) + "\t" + question_template
        return question_template_id_str

    # 根据问题模板的具体类容，构造cql语句，并查询
    def query_template(self,idx):
        # 调用问题模板类中的获取答案的方法
        try:
            answer = self.questiontemplate.get_question_answer(self.pos_quesiton, self.question_template_id_str,idx)
        except:
            answer = "我也还不知道！"
        # answer = self.questiontemplate.get_question_answer(self.pos_quesiton, self.question_template_id_str)
        return answer
