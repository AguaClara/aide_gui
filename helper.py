import os, sys, inspect, json

# Takes a relative file path (String) to the calling file and returns the correct absolute path (String). Needed to access other files within aide_gui when initialized by aide.
from os.path import join, dirname, abspath
def abs_path(file_path):
    return join(dirname(abspath(__file__)), file_path)

# Import local dependencies.
sys.path.append(abs_path('./dependencies'))
from yaml import load, dump

def load_yaml(file_path):
    """
    Returns a dictionary from a YAML file.

    Parameters
    ----------
    file_path: String
        The relative file path to the YAML file to be loaded.
    """
    with open(abs_path(file_path)) as file:
        return load(file)

def write_yaml(file_path, data):
    """
    Writes a dictionary to a YAML file.

    Parameters
    ----------
    file_path: String
        The relative file path to the YAML file to be written.
    data: dict
        The dictionary to be written to the YAML file.
    """
    with open(abs_path(file_path), 'w') as file:
        dump(data, file, default_flow_style=False)

def render_page(env, dropdown, command):
    """
    Refreshes data/display.html with the next page to be rendered.

    Parameters
    ----------
    env: Environment
        An object defined in Jinja2 that specifies a directory with list of templates.

    dropdown: dict
        Contains entries in the dropdown menu.

    command: dict
        Contains the type and data from a command sent by the HTML.
    """

    # Select the correct template given the command type.
    # NOTE: If more templates/command types are made, they must be entered in here.
    if command["action"] == 'home':
        template_name='home.html'
    elif command["action"] == 'table':
        template_name='table.html'
    elif command["action"] == 'template':
        template_name='template.html'
    else:
        template_name='home.html'

    # Compile values to be combined with the template.
    context = {'fields': command['src'], 'dropdowns': dropdown}

    # Refresh display.html with the next page to be rendered.
    with open(abs_path('data/display.html'), 'w') as display:
        display.write(env.get_template(template_name).render(context))
