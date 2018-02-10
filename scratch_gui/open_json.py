import json

# with open('new_form.json', 'r') as json_file:
#     data = json.load(json_file)
#     for param in data:
#         pName = list(param.keys())[0]
#         globals()['_%s' % pName] = "something"
#     print(data)
#     print(_flow_rate)




jstring='[{"flow_rate": [{"name": "Flow Rate (L/s)"}]}, {"sed_tank_length": [{"name": "Sed tank length (m)"}]}, {"blablabla": [{"name": "Hi There!"}]}]'

data = json.loads(jstring)
for param in data:
    pName = list(param.keys())[0]
    globals()['_%s' % pName] = "something"
print(data)
