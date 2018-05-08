import os, sys, inspect, json

def abs_path(file_path):
    """
    Takes a relative file path to the calling file and returns the correct
    absolute path. Needed because the Fusion 360 environment doesn't resolve
    relative paths well.

    Parameters
    ----------
    file_path: str
        Relative file path to the calling file

    Return
    -------
        : string
        he correct absolute path.
    """
    return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), file_path)

# add the path to local library
sys.path.append(abs_path('.'))
from . import yaml
from . import urllib3


# jinjafy given the html template with given context
def render(environment, template_name, context):
    """
    Returns a completed template string in UTF-8 encoding.

    Parameters
    ----------
    environment: Environment
        An object defined in Jinja2 library that specifies a directory with
        list of templates (including inheritance).

    template_name: string
        Name of the template file. Must exist in environment.

    context: dict
        A dictionary with key:value pairs to match template specs.

    Return
    --------
    : string
        Completed template string in UTF-8 encoding.
    """
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


def jinjafy(environment, header, command):
    """
    Outputs jinjafied.html in working directory.

    Parameters
    ----------
    environment: Environment
        An object defined in Jinja2 library that specifies a directory with
        list of templates (including inheritance)

    header: string
        Yaml that holds information for the parent template.

    command: dict
        A command of form {type: ~, link:~} to match template type to data
        collected from link.
    """
    htmlFileName='error.html'

    if command["type"] == 'home':
        htmlFileName='home.html'
    elif command["type"] == 'table':
        htmlFileName='table.html'
    elif command["type"] == 'template':
        htmlFileName='template.html'

    data = load_yaml(command["link"])
    context = {'fields': data, 'dropdowns': header}

    # render the dictionary values onto the html file
    result = render(environment, htmlFileName, context)

    # create a local html file, with jinjafied values
    with open(abs_path("jinjafied.html"), 'w') as jinjafied:
        jinjafied.write(result)
