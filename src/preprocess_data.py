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

# 角色的不同称呼
different_titles = {
    '贾宝玉': '我 宝哥哥 宝玉 宝兄弟',
    '宝玉': '我 宝哥哥 宝玉 宝兄弟',
    '林黛玉': '林妹妹 我 颦儿 林姑娘',
    '黛玉': '林妹妹 我 颦儿 林姑娘',
    '薛宝钗': '宝姐姐 宝姐姐 我 宝姑娘',
    '宝钗': '宝姐姐 宝姐姐 我 宝姑娘',
    '王熙凤':'凤姐姐 凤哥儿 凤丫头 我',
    '熙凤':'凤姐姐 凤哥儿 凤丫头 我',
    '贾母': '老太太 老太太 老太太 老太太',
    '王夫人':'母亲 舅母 姨母 太太',
    '贾政': '父亲 舅舅 姨夫 老爷',
    '贾元春':'宫里的贵妃娘娘 宫里的贵妃娘娘 宫里的贵妃娘娘 宫里的贵妃娘娘',
    '元春': '宫里的贵妃娘娘 宫里的贵妃娘娘 宫里的贵妃娘娘 宫里的贵妃娘娘',
    '贾迎春': '迎春 迎春 迎春 迎春',
    '迎春': '迎春 迎春 迎春 迎春',
    '贾探春': '探春 探春 探春 探春',
    '探春': '探春 探春 探春 探春',
    '贾惜春':'惜春 惜春 惜春 惜春',
    '惜春':'惜春 惜春 惜春 惜春',
    '史湘云': '云妹妹 云妹妹 云妹妹 史大姑娘',
    '湘云': '云妹妹 云妹妹 云妹妹 史大姑娘',
    '花袭人':  '袭人姐姐 袭人姐姐 袭姑娘 袭人' ,
    '袭人':  '袭人姐姐 袭人姐姐 袭姑娘 袭人' ,
    '秦钟': '鲸卿 秦钟 秦钟 秦钟',
    '林如海':  '姑父 父亲 林妹妹的父亲 林妹妹的父亲'
}

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

    def question_process(self, question, roleId,idx):
        # 接收问题
        self.raw_question = str(question).strip()
        # 对问题进行词性标注
        self.pos_quesiton = self.question_posseg()
        print('pos_question', self.pos_quesiton)
        # 得到问题的模板
        self.question_template_id_str = self.get_question_template()
        print('question_template_id_str', self.question_template_id_str)
        # 查询图数据库,得到答案
        self.answer = self.query_template(idx)
        if self.answer=="我也还不知道！":
            if roleId=="1":
                self.answer="好姐姐，千万绕我这一遭，原是我搞忘了!"
            elif roleId=="2":
                self.answer="我不知，想来那是件难事，岂能人人都能知晓的。"
            elif roleId=="3":
                self.answer="想来也不是件易事，你放心，赶明儿我替你问问老太太太太。"
            else:
                self.answer="此事原不该问我，改日问老太太太太便是了。"
        else:
            self.answer=self.get_answer_by_role(self.answer,roleId)
        return (self.answer)

    def question_posseg(self):
        jieba.load_userdict(USER_DICT_PATH)
        clean_question = re.sub(CLEAN_REGEX, "", self.raw_question)
        self.clean_question = clean_question
        question_seged = jieba.posseg.cut(str(clean_question))
        print("question_seged", question_seged)
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
        print('question_word', question_word)
        print('question_flag', question_flag)
        return result

    def get_question_template(self):
        # 抽象问题
        for item in ['nr', 'ns', 'ne', 'nt']:
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
    def query_template(self, idx):
        # 调用问题模板类中的获取答案的方法
        try:
            answer = self.questiontemplate.get_question_answer(self.pos_quesiton, self.question_template_id_str, idx)
        except:
            # answer = {
            #     'code': -1,
            #     'answer': "我也还不知道！"
            # }
            answer="我也还不知道！"
        return answer

    def get_answer_by_role(self,answer,roleId):
        for key in different_titles.keys():
            value=different_titles[key]
            arr=value.split(" ")
            answer=answer.replace(key,arr[int(roleId)-1])
        print(answer)
        return answer

if __name__=="__main__":
    q=Question()
    q.get_answer_by_role("宝玉到沁芳桥边桃花底下看《西厢记》，正准备将落花送进池中，黛玉说她早已准备了一个花冢，正来葬花。黛玉发现《西厢记》，宝玉借书中词句，向黛玉表白。黛玉觉得冒犯了自己尊严，引起口角，宝玉赔礼讨饶，黛玉也借《西厢记》词句，嘲笑了宝玉。于是两人收拾落花，葬到花冢里去。","1")