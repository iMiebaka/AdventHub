import json
class Payload:
    @property
    def user_list(self):
        with open("core/test/asset/test_users.json", "r") as data:
            return json.load(data)

test_data = Payload()
