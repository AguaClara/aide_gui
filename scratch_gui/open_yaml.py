import yaml

prameters={}

def outsidefunc():
    print(flow_rate)

with open("new_form.yaml", 'r') as stream:
    try:
        x=yaml.load(stream)
        # print(x)
        # print(yaml.dump(x, default_flow_style=False))
        for param in x:
            pName=list(param.keys())[0]
            globals()['%s' % pName] = 'Hello'
        outsidefunc()

    except yaml.YAMLError as exc:
        # print(exc)
        print("YAML isn't formatted correctly.")
