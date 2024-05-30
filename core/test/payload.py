import json
class Payload:
    def user_list(self, index):
        with open("core/test/asset/test_users.json", "r") as data:
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
