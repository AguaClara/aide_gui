import json

with open('/Users/eldorbekpualtov/Desktop/AguaClara/aide_gui/scratch_gui/test_gui/new_form.json', 'r') as json_file:
    data = json.load(json_file)
    print(data)
    for param in data:
        pName = list(param.keys())[0]

        pAttr = param[pName]

        globals()['_%s' % pName] = "something"

'''
#chat box:
    now that you now the structure i amthinking to create the variables with one fuction that
    first: gets the pname -- field itself -- global var pName
    second: takes the dictionary of attributes and applies each attr to global var
        for example default value
'''
# [{"flow_rate": {"name": "Flow Rate (L/s)"}}, {"sed_tank_length": {"name": "Sed tank length (m)"}}, {"blablabla": {"name": "Hi There!"}}]





# jstring='[{"flow_rate": [{"name": "Flow Rate (L/s)"}]}, {"sed_tank_length": [{"name": "Sed tank length (m)"}]}, {"blablabla": [{"name": "Hi There!"}]}]'
#
# data = json.loads(jstring)
# for param in data:
#     pName = list(param.keys())[0]
#     globals()['_%s' % pName] = "something"
# print(data)
