import json


class APIUtils:
    @classmethod
    def parse_request(cls, reqData):
        data = {}
        if reqData.method == 'POST':
            data = json.loads(reqData.get_data())
        elif reqData.method == 'GET':
            data = reqData.args
        return data
