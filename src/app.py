from flask import Flask, request, jsonify

from src import *

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/search', methods=['POST'])
def search():
    req_data = APIUtils.parse_request(request)
    return jsonify(SearchService.get_search_ans(**req_data))


if __name__ == '__main__':
    que = Question()
    res = que.question_process("章子怡演过多少部电影？")
    print(res)
    res = que.question_process("卧虎藏龙是什么类型的电影？")
    print(res)
    # app.run()
