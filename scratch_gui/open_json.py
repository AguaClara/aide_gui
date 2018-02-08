import json

data = None

with open('NEW_param.json') as json_file:
    data = json.load(json_file)
    print(data["tabs"][0]["some_design_name"])
