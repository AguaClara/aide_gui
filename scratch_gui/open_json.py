import json

with open('/Users/eldorbekpualtov/Desktop/AguaClara/aide_gui/scratch_gui/new_form.json', 'r') as json_file:
    data = json.load(json_file)

    for param in data:
        pName = list(param.keys())[0]
        pAttr = param[pName]
        globals()['_%s' % pName] = "something"
