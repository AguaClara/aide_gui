import yaml
import json


def createJSON(name, data):
    with open(name, 'w') as outfile:
        json.dump(data, outfile)


def outsidefunc():
    print(flow_rate)


with open("new_form.yaml", 'r') as stream:
    try:
        x = yaml.load(stream)
        createJSON('new_form.json', x)
        # print(x)
        # print(yaml.dump(x, default_flow_style=False))
        for param in x:
            pName = list(param.keys())[0]
            globals()['%s' % pName] = 'list of global variables are created'
        outsidefunc()

    except yaml.YAMLError as exc:
        # print(exc)
        print("YAML isn't formatted correctly.")
