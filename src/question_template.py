from query import Query
import re
import jieba.posseg
from py2neo.data import Node, Relationship, Path
import json

id_name_dic = {
    "['event']": 'eid',
    "['time']": 'tid',
    "['person']": 'pid',
    "['location']": 'lid'
}
important_relas = ['父亲', '母亲', '丈夫', '妻子', '喜欢', '参与', '参与人', '私通', '仆人', '居住地', '原籍',
                   '哥哥', '姐姐', '交好', '位于', '同宗',
                   '老师', '姬妾', '跟班', '干娘', '奶妈', '陪房', '知己', '前世', '连宗',
                   '有恩']

# 同义词
same_word = {
    '贾宝玉': ['宝玉', '贾宝玉', '宝哥哥 宝哥哥 宝玉 宝兄弟', '宝二爷', '宝玉', '怡红公子'],
    '林黛玉': ['黛玉', '林黛玉', '林妹妹 林妹妹 颦儿 林姑娘', '林姑娘', '林丫头', '潇湘妃子'],
    '薛宝钗': ['宝钗', '薛宝钗', '宝姐姐 宝姐姐 宝姐姐 宝姑娘', '宝姑娘', '宝丫头', '蘅芜君'],
    '王熙凤': ['熙凤', '王熙凤', '凤姐姐 凤哥儿 凤丫头 凤丫头', '琏二奶奶', '凤丫头', '泼皮破落户 凤辣子'],
    '贾母': ['贾母', '贾母', '老太太 老太太 老太太 老太太', '老太太', '老太太', '史太君'],
    '王夫人': ['王夫人', '王夫人', '母亲 舅母 姨母 太太', '二太太', '王夫人', '王夫人'],
    '贾政': ['贾政', '贾政', '父亲 舅舅 姨夫 老爷', '老爷', '贾政', '贾政'],
    '贾元春': ['元春', '贾元春', '宫里的贵妃娘娘 宫里的贵妃娘娘 宫里的贵妃娘娘 宫里的贵妃娘娘', '宫里的贵妃娘娘',
            '宫里的贵妃娘娘', '宫里的贵妃娘娘'],
    '贾迎春': ['迎春', '贾迎春', '迎春 迎春 迎春 迎春', '二姑娘', '二姑娘', '紫菱洲', '二木头'],
    '贾探春': ['探春', '贾探春', '探春 探春 探春 探春', '三姑娘', '三姑娘', '蕉下客'],
    '贾惜春': ['惜春', '贾惜春', '惜春 惜春 惜春 惜春', '四姑娘', '四姑娘', '藕榭'],
    '史湘云': ['湘云', '史湘云', '云妹妹 云妹妹 云妹妹 史大姑娘', '湘云', '枕霞旧友'],
    '袭人': ['袭人', '花袭人', '袭人姐姐 袭人姐姐 袭姑娘 袭人' '袭人', '袭人'],
    '秦钟': ['秦钟', '秦鲸卿', '鲸卿 秦钟 秦钟 秦钟', '秦钟', '秦钟', '秦钟'],
    '贾雨村': ['雨村', '贾雨村', '贾雨村 老师 贾雨村 贾雨村', '贾雨村', '贾雨村', '贾雨村'],
    '倪二': ['倪二', '倪二', '倪二 倪二 倪二 倪二', '倪二', '倪二', '醉金刚'],
    '林如海': ['如海', '林如海', '姑父 父亲 林妹妹的父亲 林妹妹的父亲', '姑爷', '如海', '林如海']
}

same_word_dic = {
    '宝玉': '贾宝玉', '宝哥哥': '贾宝玉', '宝兄弟': '贾宝玉', '怡红公子': '贾宝玉', '宝二爷': '贾宝玉', '混世魔王': '贾宝玉',
    '绛洞花主': '贾宝玉', '绛洞花王': '贾宝玉', '多情公子': '贾宝玉', '槛内人': '贾宝玉', '怡红院浊玉': '贾宝玉',
    '黛玉': '林黛玉', '潇湘妃子': '林黛玉', '颦儿': '林黛玉', '颦颦': '林黛玉', '林姑娘': '林黛玉', '林妹妹': '林黛玉',
    '林丫头': '林黛玉',
    '宝钗': '宝钗', '蘅芜君': '薛宝钗', '宝姐姐': '薛宝钗', '宝丫头': '薛宝钗', '宝姑娘': '薛宝钗',
    '熙凤': '王熙凤', '凤姐': '王熙凤', '凤姐儿': '王熙凤', '凤哥': '王熙凤', '凤哥儿': '王熙凤', '凤辣子': '王熙凤',
    '破落户': '王熙凤', '泼皮破落户': '王熙凤',
    '老太太': '贾母', '史太君': '贾母',
    '花袭人': '袭人',
    '林小红': '小红',
    '英莲': '香菱', '甄英莲': '香菱',
    '贾代儒夫人': '代儒夫人',
    '查抄大观园': '抄检大观园',
    '贾宝玉挨打': '宝玉挨打',
    '林黛玉葬花': '黛玉葬花',
    '湘云醉卧芍药铺': '湘云醉眠芍药裀',
    '湘云醉眠芍药裀': '湘云醉眠芍药裀',
    '湘云醉眠芍药': '湘云醉眠芍药裀',
}
dictnum = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '百': 12, '千': 13,
           '万': 14, '亿': 18, '两': 2,
           '壹': 1, '贰': 2, '叁': 3, '肆': 4, '伍': 5, '陆': 6, '柒': 7, '捌': 8, '玖': 9, '拾': 10, '佰': 12}


def getResultForDigit(a):
    count = len(a) - 1
    result = 0
    tmp = 0

    while count >= 0:
        tmpChr = a[count:count + 1]
        tmpNum = 0
        if tmpChr.isdigit():  # 防止大写数字中夹杂阿拉伯字母
            tmpNum = int(tmpChr)
        else:
            tmpNum = dictnum[tmpChr]
        if tmpNum > 10:  # 获取0的个数
            tmp = tmpNum - 10
        # 如果是个位数
        else:
            if tmp == 0:
                result += tmpNum
            else:
                result += pow(10, tmp) * tmpNum
            tmp = tmp + 1
        count = count - 1
    return result


# 具体模板中，如果idx==0 ，用于问答系统，返回一句话（由查询出来的列表包装）；
# 如果idx==1，用于语义搜索，直接返回查询出来的列表
class QuestionTemplate():
    def __init__(self):
        self.q_template_dict = {
            0: self.get_event_reason,
            1: self.get_person_ending,
            2: self.get_event_time,
            3: self.person_info,
            4: self.location_info,
            5: self.event_info,
            6: self.relation_titles,
            7: self.relation_two_people,
            8: self.live_in,
            9: self.origin,
            12:self.get_events_by_person,
            13: self.get_events_in_time,
            14: self.get_person_event
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
            # 获取地点名称
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

    # 获取人物、地点、事件的Info的通用方法
    def get_info(self, name):
        cql = f"match (m) where m.label='{name}' return m.info"
        print(cql)
        answer = self.graph.run(cql)[0]
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
        person_name = self.question_word[nr_index]
        event_name = self.question_word[nr_index] + self.question_word[v_index]
        return person_name, event_name

    def get_time(self):
        nt_index = self.question_flag.index("nt")
        time_name = self.question_word[nt_index]
        return time_name

    def get_rela_nodes(self, label, ori_label):
        content_lst = []
        for my_type in important_relas:
            cql_rela = f"match(m)-[r:{my_type}]->(n) where m.label='{label}' and n.label <> '{ori_label}' " \
                f"return n"
            answer_rela = self.graph.run(cql_rela)
            for node in answer_rela:
                ret = {}
                node = dict(node)
                ret['relation'] = my_type
                ret['title'] = node['label']
                ret['info'] = node['info']
                ret['categories'] = node['categories']
                ret['id'] = str(node[id_name_dic[node['categories']]])
                content_lst.append(ret)
            # if len(content_lst)>0: return content_lst
            # cql_rela = f"match(m)<-[r:{my_type}]-(n) where m.label='{label}' and n.label <> '{ori_label}' " \
            #     f"return n"
            # answer_rela = self.graph.run(cql_rela)
            # for node in answer_rela:
            #     ret = {}
            #     node = dict(node)
            #     ret['relation'] = "是"+my_type
            #     ret['title'] = node['label']
            #     ret['info'] = node['info']
            #     ret['categories'] = node['categories']
            #     ret['id'] = str(node[id_name_dic[node['categories']]])
            #     content_lst.append(ret)
        return content_lst

    def get_event_all(self, label):
        cql = f"match (m) where m.label='{label}' return m"
        print(cql)
        node = dict(self.graph.run(cql)[0])
        ret = {
            'title': node['label'],
            'info': node['info'],
            'categories': node['categories'],
            'id': node[id_name_dic[node['categories']]]}
        return ret
    def get_node_relation_nodes(self,node_label,relation_label):
        cql=f"match (n)-[:`{relation_label}`->(m) where n.label='{node_label}' return m]"
        ret=self.graph.run(cql)
        return ret

    # 0:ne 事件原因
    def get_event_reason(self, idx):
        # 获取事件名称，这个是在原问题中抽取的
        event_name = self.get_event_name()
        if event_name in same_word_dic.keys():
            event_name = same_word_dic[event_name]
        cql = f"match (e:Event)-[]->() where e.label='{event_name}' return e.reason"
        print(cql)
        answer = self.graph.run(cql)
        if len(answer) > 0:
            if idx == 0:
                final_answer = answer[0]
                return final_answer
            else:
                res = {
                    'answer': answer[0],
                    'contentList': self.get_rela_nodes(event_name, event_name),
                    'answerList': [],
                    'code': 2,
                    'showGraphData': {}
                }
                print('答案: {}'.format(res))
                return res
        else:
            print('[ERROR] 知识库中没有答案')
            raise Exception

    # 1:nr 人物结局
    def get_person_ending(self, idx):
        person_name = self.get_one_person_name()
        if person_name in same_word_dic.keys():
            person_name = same_word_dic[person_name]
        cql = f"match(m:Person) where m.label='{person_name}' return m.ending"
        print(cql)
        answer = self.graph.run(cql)
        print(answer)
        if len(answer) > 0:
            if idx == 0:
                final_answer = answer[0]
                return final_answer
            else:
                res = {
                    'answer': answer[0],
                    'contentList': self.get_rela_nodes(person_name, person_name),
                    'answerList': [],
                    'code': 2,
                    'showGraphData': {}
                }
                print('答案: {}'.format(res))
                return res
        else:
            print('[ERROR] 知识库中没有答案')
            raise Exception

    # 2:ne 事件在第几回
    def get_event_time(self, idx):
        # 获取事件名称，这个是在原问题中抽取的
        event_name = self.get_event_name()
        if event_name in same_word_dic.keys():
            event_name = same_word_dic[event_name]
        cql = f"match (e:Event) where e.label='{event_name}' " \
            f"match p=(e)-[r:`发生在`]->(t) return t.label"
        print(cql)
        answer = self.graph.run(cql)
        if len(answer) > 0:
            if idx == 0:
                final_answer = '{event}发生在{time}'.format(event=event_name, time=answer[0])
                return final_answer
            else:
                exts = self.get_rela_nodes(answer[0], event_name)
                exts.extend(self.get_rela_nodes(event_name, event_name))
                res = {
                    'answer': answer[0],
                    'contentList': exts,
                    'answerList': [],
                    'code': 2,
                    'showGraphData': {}
                }
                print('答案: {}'.format(res))
                return res
        else:
            print('[ERROR] 知识库中没有答案')
            raise Exception



    def chat3(self):#answerList和contentList
        person_name = self.get_one_person_name()
        if person_name in same_word_dic.keys():
            person_name = same_word_dic[person_name]
        cql=f"match(n) where n.label='{person_name}' return n.info"
        ret=self.graph.run(cql)
        if len(ret)==0: raise Exception
        else: ret=ret[0]
        final_answer = person_name + "人物简介:" + str(ret)
        return final_answer

    def search3(self):
        person_name = self.get_one_person_name()
        if person_name in same_word_dic.keys():
            person_name = same_word_dic[person_name]
        cql = f"match(n) where n.label='{person_name}' return n"
        ret = self.graph.run(cql)
        if len(ret) == 0:
            raise Exception
        else:
            ret = ret[0]
        answer_list = []
        nodeDict = dict(ret)
        answer={}
        answer['title'] = nodeDict['label']
        answer['info'] = nodeDict['info']
        answer['id'] = str(nodeDict['pid'])
        answer['categories'] = nodeDict['categories']
        answer_list.append(answer)

        res = {
            'answer': "",
            'contentList': self.get_rela_nodes(person_name,person_name),
            'answerList': answer_list,
            'code': 0,
            'showGraphData': {}
        }
        print('答案: {}'.format(res))
        return res

    # 3
    def person_info(self, idx):
        if idx==0: return self.chat3()
        else: return self.search3()

    def chat4(self):#answerList和contentList
        name = self.get_one_location_name()
        cql=f"match(n) where n.label='{name}' return n.info"
        ret=self.graph.run(cql)
        if len(ret)==0: raise Exception
        else: ret=ret[0]
        final_answer = name + "地点简介:" + str(ret)
        return final_answer

    def search4(self):
        name = self.get_one_location_name()
        cql = f"match(n) where n.label='{name}' return n"
        ret = self.graph.run(cql)
        if len(ret) == 0:
            raise Exception
        else:
            ret = ret[0]
        answer_list = []
        nodeDict = dict(ret)
        answer={}
        answer['title'] = nodeDict['label']
        answer['info'] = nodeDict['info']
        answer['id'] = str(nodeDict['lid'])
        answer['categories'] = nodeDict['categories']
        answer_list.append(answer)

        res = {
            'answer': "",
            'contentList': self.get_rela_nodes(name,name),
            'answerList': answer_list,
            'code': 0,
            'showGraphData': {}
        }
        print('答案: {}'.format(res))
        return res


    # 4
    def location_info(self, idx):
        if idx==0: return self.chat4()
        else: return self.search4()

    def chat5(self):#answerList和contentList
        name = self.get_one_event_name()
        if name in same_word_dic.keys():
            name = same_word_dic[name]
        cql=f"match(n) where n.label='{name}' return n.info"
        ret=self.graph.run(cql)
        if len(ret)==0: raise Exception
        else: ret=ret[0]
        final_answer = name + "事件简介:" + str(ret)
        return final_answer

    def search5(self):
        name = self.get_one_event_name()
        if name in same_word_dic.keys():
            name = same_word_dic[name]
        cql = f"match(n) where n.label='{name}' return n"
        ret = self.graph.run(cql)
        if len(ret) == 0:
            raise Exception
        else:
            ret = ret[0]
        answer_list = []
        answer={}
        nodeDict = dict(ret)
        answer['title'] = nodeDict['label']
        answer['info'] = nodeDict['info']
        answer['id'] = str(nodeDict['eid'])
        answer['categories'] = nodeDict['categories']
        answer_list.append(answer)

        res = {
            'answer': "",
            'contentList': self.get_rela_nodes(name,name),
            'answerList': answer_list,
            'code': 0,
            'showGraphData': {}
        }
        print('答案: {}'.format(res))
        return res

    # 5
    def event_info(self, idx):
        if idx==0: return self.chat5()
        else: return self.search5()

    def chat6(self):
        nr_name = self.get_one_person_name()
        if nr_name in same_word_dic.keys():
            nr_name = same_word_dic[nr_name]
        titles = []
        for i in range(len(self.question_flag)):
            if self.question_flag[i] == 'n':
                titles.append(self.question_word[i])
        # match (n)-[:`母亲`]->()-[:`丈夫`]->()-[:`姬妾`]->(m) where n.label='贾宝玉' return m.label
        # 贾宝玉的母亲的丈夫的姬妾是
        cql = f"match (n)-[:`{titles[0]}`]->"
        for i in range(1, len(titles)):
            cql += f"()-[:`{titles[i]}`]->"
        cql += f"(m) where n.label='{nr_name}' return m.label"
        ret = self.graph.run(cql)
        if len(ret)==0: raise Exception
        ret_set = set(ret)
        ret_list = list(ret_set)
        answer_str = "、".join(ret_list)
        final_answer_str = nr_name
        for ttl in titles:
            final_answer_str += '的' + ttl
        final_answer_str += '是' + answer_str
        return final_answer_str

    def search6(self):#answer showGraphData
        nr_name = self.get_one_person_name()
        if nr_name in same_word_dic.keys():
            nr_name = same_word_dic[nr_name]
        titles = []
        for i in range(len(self.question_flag)):
            if self.question_flag[i] == 'n':
                titles.append(self.question_word[i])

        # cql=f"match (n) where n.label='{nr_name}' return n"
        # ret=self.graph.run(cql)[0]
        # mydict=dict(ret)
        # start_node={}
        # start_node['id']=mydict['pid']
        # start_node['label'] =mydict['label']
        # start_node['nodeType'] =mydict['nodeType']
        # nodes.add(str(start_node))

        # match (n)-[:`母亲`]->()-[:`丈夫`]->()-[:`姬妾`]->(m) where n.label='贾宝玉' return m.label
        # 贾宝玉的母亲的丈夫的姬妾是
        #match p=(n)-[:`母亲`]->()-[:`丈夫`]->()-[:`姬妾`]->(m) where n.label='贾宝玉' return p,NODES(p),RELATIONSHIPS(p)

        cql = f"match (n)-[:`{titles[0]}`]->"
        for i in range(1, len(titles)):
            cql += f"()-[:`{titles[i]}`]->"
        cql += f"(m) where n.label='{nr_name}' return m"
        ret_list = self.graph.run(cql)
        if len(ret_list)==0: raise Exception
        answer_list=[]
        for ret in ret_list:
            mydict=dict(ret)
            answer={}
            answer['title']=mydict['label']
            answer['info']=mydict['info']
            answer['categories'] = mydict['categories']
            if answer['categories']=='[\'person\']':
                answer['id']=str(mydict['pid'])
            elif answer['categories']=='[\'location\']':
                answer['id']=str(mydict['lid'])
            elif answer['categories']=='[\'event\']':
                answer['id']=str(mydict['eid'])
            else:
                answer['id']=str(mydict['tid'])
            answer_list.append(answer)

        nodes = set()
        cql = f"match p=(n)-[:`{titles[0]}`]->"
        for i in range(1, len(titles)):
            cql += f"()-[:`{titles[i]}`]->"
        cql += f"(m) where n.label='{nr_name}' return NODES(p)"
        ret_list = self.graph.run(cql)
        for mynodes in ret_list:
            for node in mynodes:
                displayNode={}
                nodeDict = dict(node)
                if nodeDict['categories'] == '[\'person\']':
                    displayNode['id'] = str(nodeDict['pid'])
                elif nodeDict['categories'] == '[\'location\']':
                    displayNode['id'] = str(nodeDict['lid'])
                elif nodeDict['categories'] == '[\'event\']':
                    displayNode['id'] = str(nodeDict['eid'])
                else:
                    displayNode['id'] = str(nodeDict['tid'])
                displayNode['label'] = nodeDict['label']
                displayNode['nodeType'] = nodeDict['categories']
                nodes.add(str(displayNode))

        edges = set()
        cql = f"match p=(n)-[:`{titles[0]}`]->"
        for i in range(1, len(titles)):
            cql += f"()-[:`{titles[i]}`]->"
        cql += f"(m) where n.label='{nr_name}' return RELATIONSHIPS(p)"
        ret_list = self.graph.run(cql)
        for myedges in ret_list:
            for edge in myedges:
                displayEdge={}
                edgeDict = dict(edge)
                raw_type = str(type(edge))
                print(raw_type)
                begin = raw_type.rfind('.')
                end = raw_type.rfind('\'')
                mytype = raw_type[begin + 1:end]
                displayEdge['label'] = mytype
                displayEdge['source'] = str(edgeDict['from'])
                displayEdge['target'] = str(edgeDict['to'])
                edges.add(str(displayEdge))

        new_nodes=[]
        for ele in nodes:
            new_nodes.append(eval(ele))
        new_edges=[]
        for ele in edges:
            new_edges.append(eval(ele))
        res = {
            'answer': "",
            'contentList': [],
            'answerList': answer_list,
            'code': 1,
            'showGraphData': {
                'nodes':new_nodes,
                'edges':new_edges
            }
        }
        print('答案: {}'.format(res))
        return res

    # 6
    def relation_titles(self, idx):
        if idx==0:
            return self.chat6()
        else:
            return self.search6()

    def chat7(self):
        nr_list = []
        for i, flag in enumerate(self.question_flag):
            if flag == str('nr'):
                nr_list.append(self.question_word[i])
        if nr_list[0] in same_word_dic.keys():
            nr_list[0] = same_word_dic[nr_list[0]]
        if nr_list[1] in same_word_dic.keys():
            nr_list[1] = same_word_dic[nr_list[1]]
        cql = f"match (a:Person) where a.label='{nr_list[0]}' " \
            f"match (b:Person) where b.label='{nr_list[1]}' " \
            f"match p=shortestPath((a)-[*]->(b)) return p"
        print(cql)
        ret1 = self.graph.run(cql)
        cql = f"match (a:Person) where a.label='{nr_list[0]}' " \
            f"match (b:Person) where b.label='{nr_list[1]}' " \
            f"match p=shortestPath((b)-[*]->(a)) return p"
        print(cql)
        ret2 = self.graph.run(cql)
        ret = []
        for ele in ret1:
            ret.append(ele)
        for ele in ret2:
            ret.append(ele)
        if len(ret)==0: raise Exception
        paths=[]
        for mypath in ret:
            tmp_path=[]
            for relationship in mypath.relationships:
                raw_type = str(type(relationship))
                print(raw_type)
                begin = raw_type.rfind('.')
                end = raw_type.rfind('\'')
                mytype = raw_type[begin + 1:end]
                tmp_path.append(mytype)
            paths.append(tmp_path)
        final_answer = ""
        for path in paths:
            answer = nr_list[0]
            for title in path:
                answer += "的" + title
            answer += "是" + nr_list[1] + "。"
            final_answer += answer
        return final_answer

    def search7(self):
        nr_list = []
        for i, flag in enumerate(self.question_flag):
            if flag == str('nr'):
                nr_list.append(self.question_word[i])
        if nr_list[0] in same_word_dic.keys():
            nr_list[0] = same_word_dic[nr_list[0]]
        if nr_list[1] in same_word_dic.keys():
            nr_list[1] = same_word_dic[nr_list[1]]
        cql = f"match (a:Person) where a.label='{nr_list[0]}' " \
            f"match (b:Person) where b.label='{nr_list[1]}' " \
            f"match p=shortestPath((a)-[*]->(b)) return p"
        print(cql)
        ret1 = self.graph.run(cql)
        cql = f"match (a:Person) where a.label='{nr_list[0]}' " \
            f"match (b:Person) where b.label='{nr_list[1]}' " \
            f"match p=shortestPath((b)-[*]->(a)) return p"
        print(cql)
        ret2 = self.graph.run(cql)
        ret = []
        for ele in ret1:
            ret.append(ele)
        for ele in ret2:
            ret.append(ele)
        if len(ret)==0: raise  Exception
        nodes = set()
        edges = set()
        paths = []
        for mypath in ret:
            tmp_path = []
            for relationship in mypath.relationships:
                raw_type = str(type(relationship))
                print(raw_type)
                begin = raw_type.rfind('.')
                end = raw_type.rfind('\'')
                mytype = raw_type[begin + 1:end]
                tmp_path.append(mytype)
                #
                displayEdge = {}
                edgeDict = dict(relationship)
                displayEdge['label'] = mytype
                # displayEdge['type']=edgeDict['type']
                displayEdge['source'] = str(edgeDict['from'])
                displayEdge['target'] = str(edgeDict['to'])
                edges.add(str(displayEdge))
            paths.append(tmp_path)

        cql = f"match (a:Person) where a.label='{nr_list[0]}' " \
            f"match (b:Person) where b.label='{nr_list[1]}' " \
            f"match p=shortestPath((a)-[*]->(b)) return NODES(p)"
        print(cql)
        ret1 = self.graph.run(cql)
        cql = f"match (a:Person) where a.label='{nr_list[0]}' " \
            f"match (b:Person) where b.label='{nr_list[1]}' " \
            f"match p=shortestPath((b)-[*]->(a)) return NODES(p)"
        print(cql)
        ret2 = self.graph.run(cql)
        ret = []
        for ele in ret1:
            ret.append(ele)
        for ele in ret2:
            ret.append(ele)
        for mynodes in ret:
            for node in mynodes:
                displayNode = {}
                nodeDict = dict(node)
                displayNode['id'] = str(nodeDict['pid'])
                displayNode['label'] = nodeDict['label']
                displayNode['nodeType'] = nodeDict['categories']
                nodes.add(str(displayNode))

        final_answer = ""
        for path in paths:
            answer = nr_list[0]
            for title in path:
                answer += "的" + title
            answer += "是" + nr_list[1] + "。"
            final_answer += answer

        # answer和showGraphData
        new_nodes = []
        new_edges = []
        for ele in nodes:
            new_nodes.append(eval(ele))
        for ele in edges:
            new_edges.append(eval(ele))
        res = {
            'answer': final_answer,
            'contentList': [],
            'answerList': [],
            'code': 1,
            'showGraphData': {
                'nodes': new_nodes,
                'edges': new_edges
            }
        }
        print('答案: {}'.format(res))
        return res

    # 7
    def relation_two_people(self, idx):
        if idx==0: return self.chat7()
        else: return self.search7()
        # answer = self.graph.run(cql)
        # answer_set = set(answer)
        # answer_list = list(answer_set)
        # fret = []
        # for mypath in answer_list:
        #     ret = []
        #     for relationship in mypath.relationships:
        #         raw_type = str(type(relationship))
        #         print(raw_type)
        #         begin = raw_type.rfind('.')
        #         end = raw_type.rfind('\'')
        #         mytype = raw_type[begin + 1:end]
        #         ret.append(mytype)
        #     fret.append(ret)



    # 8

    def chat8(self):
        nr_name = self.get_one_person_name()
        if nr_name == -1:  # ns是谁的家？
            ns_name = self.get_one_location_name()
            cql = f"match (m)-[r:`居住地`]->(n) where n.label='{ns_name}' return m.label"
            print(cql)
            ret = self.graph.run(cql)
            if len(ret)==0: raise Exception
            answer_str = "、".join(ret)
            final_answer_str = answer_str + '住在' + ns_name
            return final_answer_str
        else:# nr住在哪？
            nr_name = self.get_one_person_name()
            if nr_name in same_word_dic.keys():
                nr_name = same_word_dic[nr_name]
            cql = f"match (m)-[r:`居住地`]->(n) where m.label='{nr_name}' return n.label"
            print(cql)
            ret = self.graph.run(cql)
            if len(ret)==0: raise Exception
            answer_str = "、".join(ret)
            final_answer_str = nr_name + '住在' + answer_str
            return final_answer_str

    def search8(self):
        nr_name = self.get_one_person_name()
        content_list=[]
        if nr_name == -1:  # ns是谁的家？
            ns_name = self.get_one_location_name()
            cql = f"match (m)-[r:`居住地`]->(n) where n.label='{ns_name}' return m"
            print(cql)
            ret = self.graph.run(cql)
            if len(ret) == 0: raise Exception
            answer_list=[]
            for person in ret:
                answer={}
                personNode=dict(person)
                answer['title']=personNode['label']
                answer['info']=personNode['info']
                answer['id']=str(personNode['pid'])
                answer['categories']=personNode['categories']
                answer_list.append(answer)
            if len(ret)==1:
                name=answer_list[0]['title']
                content_list=self.get_rela_nodes(name,name)
        else:# nr住在哪？
            nr_name = self.get_one_person_name()
            if nr_name in same_word_dic.keys():
                nr_name = same_word_dic[nr_name]
            cql = f"match (m)-[r:`居住地`]->(n) where m.label='{nr_name}' return n"
            print(cql)
            ret = self.graph.run(cql)
            if len(ret)==0: raise Exception
            answer_list = []
            for place in ret:
                answer = {}
                placeNode = dict(place)
                answer['title'] = placeNode['label']
                answer['info'] = placeNode['info']
                answer['id'] = str(placeNode['lid'])
                answer['categories'] = placeNode['categories']
                answer_list.append(answer)
            if len(ret) == 1:
                name=answer_list[0]['title']
                content_list = self.get_rela_nodes(name,name)
        res = {
            'answer': "",
            'contentList': content_list,
            'answerList': answer_list,
            'code': 0,
            'showGraphData': {}
        }
        print('答案: {}'.format(res))
        return res

    #8
    def live_in(self, idx):
        if idx==0:return self.chat8()
        else: return self.search8()

    def chat9(self):
        nr_name = self.get_one_person_name()
        if nr_name in same_word_dic.keys():
            nr_name = same_word_dic[nr_name]
        cql = f"match (m)-[r:`原籍`]->(n) where m.label='{nr_name}' return n.label"
        print(cql)
        ret = self.graph.run(cql)
        if len(ret)==0: raise Exception
        answer_str = "、".join(ret)
        final_answer_str = nr_name + '的原籍是' + answer_str
        return final_answer_str

    def search9(self):
        nr_name = self.get_one_person_name()
        if nr_name in same_word_dic.keys():
            nr_name = same_word_dic[nr_name]
        cql = f"match (m)-[r:`原籍`]->(n) where m.label='{nr_name}' return n"
        print(cql)
        ret = self.graph.run(cql)
        if len(ret) == 0: raise Exception
        answer_list=[]
        content_list=[]
        for place in ret:
            answer = {}
            placeNode = dict(place)
            answer['title'] = placeNode['label']
            answer['info'] = placeNode['info']
            answer['id'] = str(placeNode['lid'])
            answer['categories'] = placeNode['categories']
            answer_list.append(answer)
        if len(ret) == 1:
            name = answer_list[0]['title']
            content_list = self.get_rela_nodes(name, name)
        res = {
            'answer': "",
            'contentList': content_list,
            'answerList': answer_list,
            'code': 0,
            'showGraphData': {}
        }
        print('答案: {}'.format(res))
        return res

    # 9
    def origin(self, idx):
        if idx==0: return self.chat9()
        else: return self.search9()


    # # 10
    # def like(self, idx):
    #     person_name = self.get_one_person_name()
    #     like_idx = self.question_word.index("喜欢")
    #     nr_idx = self.question_flag.index('nr')
    #     if nr_idx < like_idx:  # nr喜欢谁
    #         cql = f"match (m)-[r:`喜欢`]->(n) where m.label='{person_name}' return n.label"
    #         print(cql)
    #         answer = self.graph.run(cql)
    #         answer_set = set(answer)
    #         answer_list = list(answer_set)
    #         if idx == 0:
    #             answer_str = "、".join(answer_list)
    #             final_answer_str = person_name + "喜欢" + answer_str
    #             return final_answer_str
    #         else:
    #             return answer_list
    #     else:  # 谁喜欢nr
    #         cql = f"match (m)-[r:`喜欢`]->(n) where n.label='{person_name}' return m.label"
    #         print(cql)
    #         answer = self.graph.run(cql)
    #         answer_set = set(answer)
    #         answer_list = list(answer_set)
    #         if idx == 0:
    #             answer_str = "、".join(answer_list)
    #             final_answer_str = answer_str + "喜欢" + person_name
    #             return final_answer_str
    #         else:
    #             return answer_list


    def chat12(self):
        nr_name=self.get_one_person_name()
        if nr_name in same_word_dic.keys():
            nr_name = same_word_dic[nr_name]
        cql=f"match (n)-[:`参与`]->(m:Event) where n.label='{nr_name}' return m.label"
        ret=self.graph.run(cql)
        if len(ret) == 0: raise Exception
        answer="、".join(ret)
        final_answer=nr_name+"参与的事件有"+answer
        return final_answer

    def search12(self):
        nr_name = self.get_one_person_name()
        if nr_name in same_word_dic.keys():
            nr_name = same_word_dic[nr_name]
        cql = f"match (n)-[:`参与`]->(m:Event) where n.label='{nr_name}' return m"
        ret = self.graph.run(cql)
        if len(ret)==0: raise Exception
        answer_list=[]
        for event in ret:
            answer={}
            eventNode=dict(event)
            answer['title']=eventNode['label']
            answer['info']=eventNode['info']
            answer['id']=str(eventNode['eid'])
            answer['categories']=eventNode['categories']
            answer_list.append(answer)
        content_list=[]
        if len(answer_list)==1:
            content_list=self.get_rela_nodes(answer['title'],answer['title'])
        res = {
            'answer': "",
            'contentList': content_list,
            'answerList': answer_list,
            'code': 0,
            'showGraphData': {}
        }
        print('答案: {}'.format(res))
        return res

    #12
    def get_events_by_person(self,idx):
        if idx==0: return self.chat12()
        else: return self.search12()


    # # 11
    # def help(self, idx):
    #     nr_idx = self.question_flag.index("nr")
    #     r_idx = self.question_flag.index("r")
    #     nr_name = self.question_word[nr_idx]
    #     if r_idx < nr_idx:  # 谁是贾宝玉的恩人
    #         cql = f"match (m)-[r:`有恩`]->(n) where n.label='{nr_name}' return m.label"
    #         print(cql)
    #         answer = self.graph.run(cql)
    #         answer_set = set(answer)
    #         answer_list = list(answer_set)
    #         if idx == 0:  # chat
    #             answer_str = "、".join(answer_list)
    #             final_answer_str = answer_str + "有恩于" + nr_name
    #             return final_answer_str
    #         else:
    #             return answer_list
    #     else:  # 贾宝玉是谁的恩人
    #         cql = f"match (m)-[r:`有恩`]->(n) where m.label='{nr_name}' return n.label"
    #         print(cql)
    #         answer = self.graph.run(cql)
    #         answer_set = set(answer)
    #         answer_list = list(answer_set)
    #         if idx == 0:  # chat
    #             answer_str = "、".join(answer_list)
    #             final_answer_str = nr_name + "有恩于" + answer_str
    #             return final_answer_str
    #         else:
    #             return answer_list

    # 13:nt 第几回发生了什么事件
    def get_events_in_time(self, idx):
        time = self.get_time()
        num = re.sub(r'\D', "", time)
        # 如果该文件名有数字，则读取该文件
        if str(num).strip() == "":
            # 中文数字
            digit = getResultForDigit(time[1:-1])
            time = '第{}回'.format(digit)
        cql = f"match (t:Time) where t.label='{time}' " \
            f"match p=(e)-[r:`发生在`]->(t) return e.label"
        print(cql)
        answer = self.graph.run(cql)
        if len(answer) > 0:
            if idx == 0:
                final_answer = "{time}发生的主要事件有" + '、'.join(answer)
                return final_answer
            else:
                answer_lst = []
                content_lst = []
                final_answer = answer
                for e in final_answer:
                    e_answer = self.get_event_all(e)
                    answer_lst.append(e_answer)
                title_set = set()
                for event_name in final_answer:
                    ext = self.get_rela_nodes(event_name, event_name)
                    for i in ext:
                        if i['title'] not in title_set:
                            title_set.add(i['title'])
                            content_lst.append(i)
                res = {
                    'answer': '',
                    'contentList': content_lst,
                    'answerList': answer_lst,
                    'code': 0,
                    'showGraphData': {}
                }
                print('答案: {}'.format(res))
                return res
        else:
            print('[ERROR] 知识库中没有答案')
            raise Exception

    # 14:nr v人物为什么事件
    def get_person_event(self, idx):
        # 获取事件名称，这个是在原问题中抽取的
        person_name, event_name = self.get_sep_event_name()
        if event_name in same_word_dic.keys():
            event_name = same_word_dic[event_name]
        cql = f"match (e:Event)-[]->() where e.label='{event_name}' return e.reason"
        print(cql)
        answer = self.graph.run(cql)
        if len(answer) > 0:
            if idx == 0:
                final_answer = answer[0]
                return final_answer
            else:
                res = {
                    'answer': answer[0],
                    'contentList': self.get_rela_nodes(event_name, event_name),
                    'answerList': [],
                    'code': 2,
                    'showGraphData': {}
                }
                print('答案: {}'.format(res))
                return res
        else:
            print('[ERROR] 知识库中没有答案')
            raise Exception


if __name__ == '__main__':
    # question_flag=['nr','ns','nt','你好']
    # try:
    #     tag_index = question_flag.index("ne")
    #     print(tag_index)
    # except:
    #     print('exception')
    q1 = "谁是贾宝玉"
    question_seged = jieba.posseg.cut(q1)
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

    q2 = "贾宝玉帮助过什么人"
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

    q4 = "贾宝玉的母亲的哥哥的妻子的丈夫的老师的姐姐的干娘的姬妾是谁"
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
