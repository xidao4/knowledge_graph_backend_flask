from flask import Flask, request, jsonify

from services import *
from utils import APIUtils

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/chat/getAnswer', methods=['POST'])
def chat_getAnswer():
    req_data = APIUtils.parse_request(request)
    return jsonify(SearchService.get_chat_ans(**req_data))


@app.route('/search/getAnswer',methods=['POST'])
def search_getAnswer():
    req_data=APIUtils.parse_request(request)
    return jsonify(SearchService.get_search_ans(**req_data))

if __name__ == '__main__':
    # que = Question()
    # res = que.question_process("章子怡演过多少部电影？")
    # print(res)
    # res = que.question_process("卧虎藏龙是什么类型的电影？")
    # print(res)
    app.run(host="0.0.0.0", port=5000, debug=True)
