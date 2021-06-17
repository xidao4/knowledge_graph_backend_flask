"""
9:nnt 参演评分 小于 x
10:nnt 电影类型
11:nnt nnr 合作 电影列表
12:nnt 电影数量
13:nnt 出生日期
"""
from query import Query
import re
import jieba.posseg
from py2neo.data import Node, Relationship


# 具体模板中，如果idx==0 ，用于问答系统，返回一句话（由查询出来的列表包装）；
# 如果idx==1，用于语义搜索，直接返回查询出来的列表
class QuestionTemplate():
    def __init__(self):
        self.q_template_dict = {
            0: self.get_event_reason,
            1: self.get_person_ending,
            3: self.person_info,
            4: self.location_info,
            5: self.event_info,
            6: self.relation_titles,
            7: self.relation_two_people,
<<<<<<< HEAD
            12:self.like,
            14: self.get_person_event
=======
            8: self.live_in,
            9: self.origin,
            10:self.like,
            11:self.help
>>>>>>> 8a2fa0cf0f9ca81d43b089bf0e7817258a275f79
        }
        # self.titles=['哥哥','姐姐','姬妾']
        # self.revers=['弟弟','','丈夫']
        # 连接数据库
        self.graph = Query()
        # 测试数据库是否连接上
        # result=self.graph.run("match (m:Movie)-[]->() where m.title='卧虎藏龙' return m.rating")
        # print(result)
        # exit()




    def get_question_answer(self, question, template, idx):
        # 如果问题模板的格式不正确则结束
        assert len(str(template).strip().split("\t")) == 2
        template_id, template_str = int(str(template).strip().split("\t")[0]), str(template).strip().split("\t")[1]
        self.template_id = template_id
        # self.template_str2list = str(template_str).split()

        # 预处理问题
        question_word, question_flag = [], []
        for one in question:
            word, flag = one.split("/")
            question_word.append(str(word).strip())
            question_flag.append(str(flag).strip())
        assert len(question_flag) == len(question_word)
        self.question_word = question_word
        self.question_flag = question_flag
        self.raw_question = question
        # 根据问题模板来做对应的处理，获取答案
        answer = self.q_template_dict[template_id](idx)
        return answer


    # 获取人物名字
    def get_one_person_name(self):
        # 获取nm在原问题中的下标
        try:
            tag_index = self.question_flag.index("nr")
            # 获取人物名称
            name = self.question_word[tag_index]
            return name
        except:
            return "-1"

    # 获取地点名字
    def get_one_location_name(self):
        # 获取ns在原问题中的下标
        try:
            tag_index = self.question_flag.index("ns")
            #获取地点名称
            name = self.question_word[tag_index]
            return name
        except:
            return -1

    # 获取事件名字
    def get_one_event_name(self):
        # 获取ne在原问题中的下标
        try:
            tag_index = self.question_flag.index("ne")
            # 获取事件名称
            name = self.question_word[tag_index]
            return name
        except:
            return -1

    #获取人物、地点、事件的Info的通用方法
    def get_info(self,name):
        cql = f"match (m) where m.label='{name}' return m.info"
        print(cql)
        answer = self.graph.run(cql)[0]
        return answer

    #3
    def person_info(self,idx):
        person_name=self.get_one_person_name()
        if idx==1:
            answer_lst = []
            answer_lst.append(person_name)
            return answer_lst

        answer = self.get_info(person_name)
        print(answer)
        final_answer = person_name + "人物简介:" + str(answer)
        return final_answer

    # 4
    def location_info(self, idx):
        location_name = self.get_one_location_name()
        if idx == 1:
            answer_lst = []
            answer_lst.append(location_name)
            return answer_lst

        answer = self.get_info(location_name)
        print(answer)
        final_answer = location_name + "地点简介:" + str(answer)
        return final_answer

    # 5
    def event_info(self, idx):
        event_name = self.get_one_event_name()
        if idx == 1:
            answer_lst = []
            answer_lst.append(event_name)
            return answer_lst

        answer = self.get_info(event_name)
        print(answer)
        final_answer = event_name + "事件简介:" + str(answer)
        return final_answer

    #6
    def relation_titles(self,idx):
        nr_name=self.get_one_person_name()
        titles=[]
        for i in range(len(self.question_flag)):
            if self.question_flag[i]=='n':
                titles.append(self.question_word[i])
        #match (n)-[:`母亲`]->()-[:`丈夫`]->()-[:`姬妾`]->(m) where n.label='贾宝玉' return m.label
        #贾宝玉的母亲的丈夫的姬妾是
        print(titles)
        cql = f"match (n)-[:`{titles[0]}`]->"
        for i in range(1,len(titles)):
            cql+=f"()-[:`{titles[i]}`]->"
        cql+=f"(m) where n.label='{nr_name}' return m.label"
        print(cql)
        answer = self.graph.run(cql)
        answer_set = set(answer)
        answer_list = list(answer_set)
        if idx == 1:  # search
            return answer_list
        else:
            answer_str = "、".join(answer_list)
            final_answer_str =  nr_name
            for ttl in titles:
                final_answer_str+='的'+ttl
            final_answer_str+='是' + answer_str
            return final_answer_str

    #7
    def relation_two_people(self,idx):
        nr_list = []
        for i, flag in enumerate(self.question_flag):
            if flag == str('nr'):
                nr_list.append(self.question_word[i])
        cql=f"match (a:Person) where a.label='{nr_list[0]}' " \
            f"match (b:Person) where b.label='{nr_list[1]}' " \
            f"match p=(a)-[*..5]->(b) return p,relations(p)"
        print(cql)
        answer = self.graph.run(cql)
        answer_set = set(answer)
        answer_list = list(answer_set)
        fret=[]
        for mymap in answer_list:
            segments=mymap["segments"]
            ret=[]
            for segment in segments:
                rel=segment["relationship"]["type"]
                ret.append(rel)
            fret.append(ret)
        if idx==1: return fret

        final_answer=""
        for ret in fret:
            answer=nr_list[0]
            for title in ret:
                answer+="的"+title
            answer+="是"+nr_list[1]+"。"
            final_answer+=answer
        return answer

    #8
    def live_in(self,idx):
        #nr住在哪？
        nr_name=self.get_one_person_name()
        if nr_name==-1:#ns是谁的家？
            ns_name=self.get_one_location_name()
            cql = f"match (m)-[r:`居住地`]->(n) where n.label='{ns_name}' return m.label"
            print(cql)
            answer = self.graph.run(cql)
            answer_set = set(answer)
            answer_list = list(answer_set)
            if idx==1:#search
                return answer_list
            else:
                answer_str = "、".join(answer_list)
                final_answer_str =  answer_str+'住在'+ns_name
                return final_answer_str
        else:#nr住在哪？
            nr_name = self.get_one_person_name()
            cql = f"match (m)-[r:`居住地`]->(n) where m.label='{nr_name}' return n.label"
            print(cql)
            answer = self.graph.run(cql)
            answer_set = set(answer)
            answer_list = list(answer_set)
            if idx==1:#search
                return answer_list
            else:#chat
                answer_str = "、".join(answer_list)
                final_answer_str =  nr_name+'住在'+answer_str
                return final_answer_str

    #9
    def origin(self,idx):
        nr_name=self.get_one_person_name()
        cql = f"match (m)-[r:`原籍`]->(n) where m.label='{nr_name}' return n.label"
        print(cql)
        answer = self.graph.run(cql)
        answer_set = set(answer)
        answer_list = list(answer_set)
        if idx == 1:  # search
            return answer_list
        else:
            answer_str = "、".join(answer_list)
            final_answer_str = nr_name + '的原籍是' + answer_str
            return final_answer_str

    #10
    def like(self,idx):
        person_name=self.get_one_person_name()
        like_idx=self.question_word.index("喜欢")
        nr_idx=self.question_flag.index('nr')
        if nr_idx<like_idx:#nr喜欢谁
            cql = f"match (m)-[r:`喜欢`]->(n) where m.label='{person_name}' return n.label"
            print(cql)
            answer = self.graph.run(cql)
            answer_set = set(answer)
            answer_list = list(answer_set)
            if idx==0:
                answer_str = "、".join(answer_list)
                final_answer_str=person_name+"喜欢"+answer_str
                return final_answer_str
            else:
                return answer_list
        else:#谁喜欢nr
            cql = f"match (m)-[r:`喜欢`]->(n) where n.label='{person_name}' return m.label"
            print(cql)
            answer = self.graph.run(cql)
            answer_set = set(answer)
            answer_list = list(answer_set)
            if idx==0:
                answer_str = "、".join(answer_list)
                final_answer_str=answer_str+"喜欢"+person_name
                return final_answer_str
            else:
                return answer_list

<<<<<<< HEAD
    def get_question_answer(self, question, template,idx):
        # 如果问题模板的格式不正确则结束
        assert len(str(template).strip().split("\t")) == 2
        template_id, template_str = int(str(template).strip().split("\t")[0]), str(template).strip().split("\t")[1]
        self.template_id = template_id
        #self.template_str2list = str(template_str).split()

        # 预处理问题
        question_word, question_flag = [], []
        for one in question:
            word, flag = one.split("/")
            question_word.append(str(word).strip())
            question_flag.append(str(flag).strip())
        assert len(question_flag) == len(question_word)
        self.question_word = question_word
        self.question_flag = question_flag
        self.raw_question = question
        # 根据问题模板来做对应的处理，获取答案
        answer = self.q_template_dict[template_id](idx)
        return answer

    # 获取事件名称
    def get_event_name(self):
        # 获取ne在原问题中的下标
        tag_index = self.question_flag.index("ne")
        # 获取事件名称
        event_name = self.question_word[tag_index]
        return event_name

    def get_sep_event_name(self):
        # 获取nr、v在原问题中的下标
        nr_index = self.question_flag.index("nr")
        v_index = self.question_flag.index("v")
        # 拼接得到事件名称
        event_name = self.question_word[nr_index] + self.question_word[v_index]
        return event_name

    def get_name(self, type_str):
        name_count = self.question_flag.count(type_str)
        if name_count == 1:
            ## 获取nm在原问题中的下标
            tag_index = self.question_flag.index(type_str)
            ## 获取电影名称
            name = self.question_word[tag_index]
            return name
        else:
            result_list = []
            for i, flag in enumerate(self.question_flag):
                if flag == str(type_str):
                    result_list.append(self.question_word[i])
            return result_list

    def get_num_x(self):
        x = re.sub(r'\D', "", "".join(self.question_word))
        return x

    # 0:ne 事件原因
    def get_event_reason(self):
        # 获取事件名称，这个是在原问题中抽取的
        event_name = self.get_event_name()
        cql = f"match (e:Event)-[]->() where e.label='{event_name}' return e.reason"
        print(cql)
        answer = self.graph.run(cql)
        if len(answer) > 0:
            final_answer = answer[0]
            print('答案: {}'.format(final_answer))
            return final_answer
        else:
            print('[ERROR] 知识库中没有答案')
            raise Exception

    # 1:nr 人物结局
    def get_person_ending(self):
        movie_name = self.get_event_name()
        cql = f"match(m:Movie)-[]->() where m.title='{movie_name}' return m.releasedate"
        print(cql)
        answer = self.graph.run(cql)[0]
        final_answer = movie_name + "的上映时间是" + str(answer) + "！"
        return final_answer

    # 2:nm 类型
    def get_movie_type(self):
        movie_name = self.get_event_name()
        cql = f"match(m:Movie)-[r:is]->(b) where m.title='{movie_name}' return b.name"
        print(cql)
        answer = self.graph.run(cql)
        answer_set = set(answer)
        answer_list = list(answer_set)
        answer = "、".join(answer_list)
        final_answer = movie_name + "是" + str(answer) + "等类型的电影！"
        return final_answer

    # 3:nm 简介
    def get_movie_introduction(self):
        movie_name = self.get_event_name()
        cql = f"match(m:Movie)-[]->() where m.title='{movie_name}' return m.introduction"
        print(cql)
        answer = self.graph.run(cql)[0]
        final_answer = movie_name + "主要讲述了" + str(answer) + "！"
        return final_answer

    # 4:nm 演员列表
    def get_movie_actor_list(self):
        movie_name = self.get_event_name()
        cql = f"match(n:Person)-[r:actedin]->(m:Movie) where m.title='{movie_name}' return n.name"
        print(cql)
        answer = self.graph.run(cql)
        answer_set = set(answer)
        answer_list = list(answer_set)
        answer = "、".join(answer_list)
        final_answer = movie_name + "由" + str(answer) + "等演员主演！"
        return final_answer

    # 5:nnt 介绍
    def get_actor_info(self):
        actor_name = self.get_name('nr')
        cql = f"match(n:Person)-[]->() where n.name='{actor_name}' return n.biography"
        print(cql)
        answer = self.graph.run(cql)[0]
        final_answer = answer
        return final_answer

    # 6:nnt ng 电影作品
    def get_actor_act_type_movie(self):
        actor_name = self.get_name("nr")
        type = self.get_name("ng")
        # 查询电影名称
        cql = f"match(n:Person)-[]->(m:Movie) where n.name='{actor_name}' return m.title"
        print(cql)
        movie_name_list = list(set(self.graph.run(cql)))
        # 查询类型
        result = []
        for movie_name in movie_name_list:
            movie_name = str(movie_name).strip()
            try:
                cql = f"match(m:Movie)-[r:is]->(t) where m.title='{movie_name}' return t.name"
                # print(cql)
                temp_type = self.graph.run(cql)
                if len(temp_type) == 0:
                    continue
                if type in temp_type:
                    result.append(movie_name)
            except:
                continue
        answer = "、".join(result)
        print(answer)
        final_answer = actor_name + "演过的" + type + "电影有:\n" + answer + "。"
        return final_answer

    # 7:nnt 电影作品
    def get_actor_act_movie_list(self):
        actor_name = self.get_name("nr")
        answer_list = self.get_actorname_movie_list(actor_name)
        answer = "、".join(answer_list)
        final_answer = actor_name + "演过" + str(answer) + "等电影！"
        return final_answer

    def get_actorname_movie_list(self, actorname):
        # 查询电影名称
        cql = f"match(n:Person)-[]->(m:Movie) where n.name='{actorname}' return m.title"
        print(cql)
        answer = self.graph.run(cql)
        answer_set = set(answer)
        answer_list = list(answer_set)
        return answer_list

    # 8:nnt 参演评分 大于 x
    def get_movie_rating_bigger(self):
        actor_name = self.get_name('nr')
        x = self.get_num_x()
        cql = f"match(n:Person)-[r:actedin]->(m:Movie) where n.name='{actor_name}' and m.rating>={x} return m.title"
        print(cql)
        answer = self.graph.run(cql)
        answer = "、".join(answer)
        answer = str(answer).strip()
        final_answer = actor_name + "演的电影评分大于" + x + "分的有" + answer + "等！"
        return final_answer

    def get_movie_rating_smaller(self):
        actor_name = self.get_name('nr')
        x = self.get_num_x()
        cql = f"match(n:Person)-[r:actedin]->(m:Movie) where n.name='{actor_name}' and m.rating<{x} return m.title"
        print(cql)
        answer = self.graph.run(cql)
        answer = "、".join(answer)
        answer = str(answer).strip()
        final_answer = actor_name + "演的电影评分小于" + x + "分的有" + answer + "等！"
        return final_answer

    def get_actor_movie_type(self):
        actor_name = self.get_name("nr")
        # 查询电影名称
        cql = f"match(n:Person)-[]->(m:Movie) where n.name='{actor_name}' return m.title"
        print(cql)
        movie_name_list = list(set(self.graph.run(cql)))
        # 查询类型
        result = []
        for movie_name in movie_name_list:
            movie_name = str(movie_name).strip()
            try:
                cql = f"match(m:Movie)-[r:is]->(t) where m.title='{movie_name}' return t.name"
                # print(cql)
                temp_type = self.graph.run(cql)
                if len(temp_type) == 0:
                    continue
                result += temp_type
            except:
                continue
        answer = "、".join(list(set(result)))
        print(answer)
        final_answer = actor_name + "演过的电影有" + answer + "等类型。"
        return final_answer
=======
    #11
    def help(self,idx):
        nr_idx = self.question_flag.index("nr")
        r_idx=self.question_flag.index("r")
        nr_name = self.question_word[nr_idx]
        if r_idx<nr_idx:#谁是贾宝玉的恩人
            cql = f"match (m)-[r:`有恩`]->(n) where n.label='{nr_name}' return m.label"
            print(cql)
            answer = self.graph.run(cql)
            answer_set = set(answer)
            answer_list = list(answer_set)
            if idx==0: #chat
                answer_str = "、".join(answer_list)
                final_answer_str=answer_str+"有恩于"+nr_name
                return final_answer_str
            else:
                return answer_list
        else:#贾宝玉是谁的恩人
            cql = f"match (m)-[r:`有恩`]->(n) where m.label='{nr_name}' return n.label"
            print(cql)
            answer = self.graph.run(cql)
            answer_set = set(answer)
            answer_list = list(answer_set)
            if idx == 0:  # chat
                answer_str = "、".join(answer_list)
                final_answer_str = nr_name + "有恩于" + answer_str
                return final_answer_str
            else:
                return answer_list
>>>>>>> 8a2fa0cf0f9ca81d43b089bf0e7817258a275f79



<<<<<<< HEAD
    def get_actor_birthday(self):
        actor_name = self.get_name('nr')
        cql = f"match(n:Person)-[]->() where n.name='{actor_name}' return n.birth"
        print(cql)
        answer = self.graph.run(cql)[0]
        final_answer = actor_name + "的生日是" + answer + "。"
        return final_answer

    # 14:nr v人物事件
    def get_person_event(self):
        # 获取事件名称，这个是在原问题中抽取的
        event_name = self.get_sep_event_name()
        cql = f"match (e:Event)-[]->() where e.label='{event_name}' return e.reason"
        print(cql)
        answer = self.graph.run(cql)
        if len(answer) > 0:
            final_answer = answer[0]
            print('答案: {}'.format(final_answer))
            return final_answer
        else:
            print('[ERROR] 知识库中没有答案')
            raise Exception
=======
if __name__=='__main__':
    # question_flag=['nr','ns','nt','你好']
    # try:
    #     tag_index = question_flag.index("ne")
    #     print(tag_index)
    # except:
    #     print('exception')
    q1="谁帮助过贾宝玉"
    question_seged = jieba.posseg.cut(q1)
    result,question_word,question_flag=[],[],[]
    for w in question_seged:
        temp_word = f"{w.word}/{w.flag}"
        result.append(temp_word)
        # 预处理问题
        word, flag = w.word, w.flag
        question_word.append(str(word).strip())
        question_flag.append(str(flag).strip())
    print(question_word)
    print(question_flag)

    q2="贾宝玉帮助过什么人"
    question_seged = jieba.posseg.cut(q2)
    result, question_word, question_flag = [], [], []
    for w in question_seged:
        temp_word = f"{w.word}/{w.flag}"
        result.append(temp_word)
        # 预处理问题
        word, flag = w.word, w.flag
        question_word.append(str(word).strip())
        question_flag.append(str(flag).strip())
    print(question_word)
    print(question_flag)

    q3 = "贾宝玉帮助过哪些人"
    question_seged = jieba.posseg.cut(q3)
    result, question_word, question_flag = [], [], []
    for w in question_seged:
        temp_word = f"{w.word}/{w.flag}"
        result.append(temp_word)
        # 预处理问题
        word, flag = w.word, w.flag
        question_word.append(str(word).strip())
        question_flag.append(str(flag).strip())
    print(question_word)
    print(question_flag)

    q4="贾宝玉的母亲的哥哥的妻子的丈夫的老师的姐姐的干娘的姬妾是谁"
    jieba.load_userdict("../data/userdict3.txt")
    question_seged = jieba.posseg.cut(q4)
    result, question_word, question_flag = [], [], []
    for w in question_seged:
        temp_word = f"{w.word}/{w.flag}"
        result.append(temp_word)
        # 预处理问题
    #     word, flag = w.word, w.flag
    #     question_word.append(str(word).strip())
    #     question_flag.append(str(flag).strip())
    # print(question_word)
    # print(question_flag)
    print(result)
    # ['谁', '帮助', '过', '贾宝玉']
    # ['r', 'v', 'ug', 'nr']
    # ['贾宝玉', '帮助', '过', '什么', '人']
    # ['nr', 'v', 'ug', 'r', 'n']
    # ['贾宝玉', '帮助', '过', '哪些', '人']
    # ['nr', 'v', 'ug', 'r', 'n']
>>>>>>> 8a2fa0cf0f9ca81d43b089bf0e7817258a275f79
