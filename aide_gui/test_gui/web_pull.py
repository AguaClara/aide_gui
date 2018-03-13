
# try:
#     with open("form.txt", "r") as url:
#         url = (url.read()).strip()
#         http = urllib3.PoolManager()
#         r = http.request('GET', url)
#         r.data.decode('utf-8')
#         globals()["yaml_form"]=yaml.load(r.data.decode('utf-8'))
# except:
#     pass
#
# print(yaml_form)
def load_yaml():
    try:
        with open("form.txt", "r") as url:
            url = (url.read()).strip()
            http = urllib3.PoolManager()
            r = http.request('GET', url)
            r.data.decode('utf-8')
            globals()["yaml_form"]yaml.load(r.data.decode('utf-8'))
        except:
            try:
                with open(abs_path("form.txt")) as fp:
                    globals()['yaml_form'] = yaml.load(fp)
            except:
                if _ui:
                    _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
