import yaml
import json

<<<<<<< HEAD

=======
>>>>>>> e5b3cc62d1f0d88cb3be879461edbc1955b4b560
def outsidefunc():
    print(flow_rate)


def createJSON(name, data):
    with open(name, 'w') as outfile:
        json.dump(data, outfile)

with open("new_form.yaml", 'r') as stream:
    try:
        x = yaml.load(stream)
        createJSON('new_form.json', x)
        # print(x)
        # print(yaml.dump(x, default_flow_style=False))
        for param in x:
            pName = list(param.keys())[0]
            globals()['%s' % pName] = 'Hello'
        outsidefunc()

    except yaml.YAMLError as exc:
        # print(exc)
        print("YAML isn't formatted correctly.")
