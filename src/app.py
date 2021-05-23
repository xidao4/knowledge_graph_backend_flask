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
    app.run()
