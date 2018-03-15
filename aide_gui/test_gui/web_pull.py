
import urllib3
import yaml

def load_yaml():
    try:
        with open("form.txt", "r") as fp:
            v = yaml.load(fp)
            print(type(v))
            if (type(v) != list and type(v) != dict):
                print("inside if")
                raise Exception('This is not a YAML')
            globals()['yaml_form'] = v
    except:
        try:
            with open("form.txt", "r") as url:
                url = (url.read()).strip()
                http = urllib3.PoolManager()
                r = http.request('GET', url)
                status = r.status # check URL status
                if (status != 200):
                    raise Exception('This is not a URL')
                globals()["yaml_form"] = yaml.load(r.data.decode('utf-8'))
        except:
            print('Not a YAML or URL')

load_yaml()
# print(globals())
# print(type(yaml_form))
# print(yaml_form)
