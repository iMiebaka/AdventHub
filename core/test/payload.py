import json
class Payload:
    def __init__(self) -> None:
        with open("core/test/asset/auth.json", "w") as data:
            json.dump([], data, indent=4)

    def user_list(self, index):
        with open("core/test/asset/test_users.json", "r") as data:
            if type(index) == int:
                return json.load(data)[index]
            return json.load(data)

    def write_token(self, token):
        with open("core/test/asset/auth.json", "w") as data:
            json.dump( token, data, indent=4)

    def read_token(self, index):
        with open("core/test/asset/auth.json", "r") as data:
            if type(index) == int:
                return json.load(data)[index]
            return json.load(data)

    def comment_list(self, index):
        with open("core/test/asset/comments.json", "r") as data:
            if type(index) == int:
                return json.load(data)[index]
            return json.load(data)

    @property
    def exhortation_list(self):
        with open("core/test/asset/exhortation.json", "r") as data:
            return json.load(data)

test_data = Payload()
