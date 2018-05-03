import os, sys, inspect, json
# returns absolute path
def abs_path(file_path):
    return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), file_path)

# add the path to local library
sys.path.append(abs_path('.'))
from . import yaml
from . import urllib3


# jinjafy given the html template with given context
def render(environment, template_name, context):
    return environment.get_template(template_name).render(context)


# load yaml from path
def load_yaml(fpath):
    """
    Returns a yaml form structure or None, if error occurred

    Parameters
    ----------
    fpath: str
        The local file path/URL for the yaml to be retrieved from

    Return
    --------
    yam: dict
        A dictionary thats extrapolated from yaml format
    """
    # If yaml is retrieved from user's local path
    try:
        with open(abs_path(fpath)) as fp:
            yam = yaml.load(fp)
            if (type(yam) != list and type(yam) != dict):
                raise Exception('This is not a YAML')
            return  yam
    except:
        # If yaml is retrieved from a given url
        try:
            url = fpath.strip()
            http = urllib3.PoolManager()
            r = http.request('GET', url)
            status = r.status # check URL status
            if (status != 200):
                raise Exception('This is not a URL')
            yam =  yaml.load(r.data.decode('utf-8'))
            return yam
        except:
            return None

# given environment with path to jinjafiable html files, header (a yaml data),
# command (type: ~, src: ~) to match template to link data to, output jinjafied.html
def jinjafy(environment, header, command):
    data = load_yaml(command["link"])
    context = {'fields': data, 'dropdowns': header}

    htmlFileName='error.html'

    if command["type"] == 'home':
        htmlFileName='home.html'
    elif command["type"] == 'table':
        htmlFileName='table.html'
    elif command["type"] == 'template':
        htmlFileName='template.html'

    # render the dictionary values onto the html file
    result = render(environment, htmlFileName, context)

    # create a local html file, with jinjafied values
    with open(abs_path("jinjafied.html"), 'w') as jinjafied:
        jinjafied.write(result)
