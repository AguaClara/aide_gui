filepath="/Users/eldorbekpualtov/Desktop/AguaClara/aide_gui/scratch_gui/test_gui"


sys.path.append("/Users/path-name/.local/lib/python3.6/site-packages")


def abs_path(file_path):
    """
    Takes a relative file path to the calling file and returns the correct
    absolute path.
    Needed because the Fusion 360 environment doesn't resolve relative paths
    well.
    """
    return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), file_path)

# parses json and for each key; creates a global in format: _[pName]
# always add absolute path to the json file
def createGLOBAL():
    #./Users/eldorbekpualtov/Desktop/AguaClara/aide_gui/scratch_gui/test_gui/
    with open('./resources/AIDE/new_form.json', 'r') as json_file:
        data = json.loads(json_file)
        for param in data:
            pName = list(param.keys())[0]
            globals()['_%s' % pName] = "something"

    # jstring='[{"flow_rate": [{"name": "Flow Rate (L/s)"}]}, {"sed_tank_length": [{"name": "Sed tank length (m)"}]}, {"blablabla": [{"name": "Hi There!"}]}]'
    # data = json.loads(jstring)
    # for param in data:
    #     pName = list(param.keys())[0]
    #     globals()['_%s' % pName] =  "something"
