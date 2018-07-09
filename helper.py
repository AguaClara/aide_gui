import sys
from os.path import join, dirname, abspath

def abs_path(file_path):
    """
    Returns the absolute path from the file that calls this function to file_path. Needed to access other files within aide_gui when initialized by aide.

    Parameters
    ----------
    file_path: String
        The relative file path from the file that calls this function.
    """

    return join(dirname(abspath(__file__)), file_path)

# Import local dependencies.
sys.path.append(abs_path('./dependencies'))
import yaml

def load_yaml(file_path):
    """
    Returns a dictionary from a YAML file.

    Parameters
    ----------
    file_path: String
        The relative file path to the YAML file to be loaded.
    """

    with open(abs_path(file_path)) as file:
        return yaml.load(file)

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
        yaml.dump(data, file, default_flow_style=False)

def render_page(env, dropdown, command):
    """
    Refreshes data/displayed_page.html with the next page to be rendered.

    Parameters
    ----------
    env: Environment
        An object defined in Jinja2 that specifies a directory with list of templates.

    dropdown: dict
        Contains entries in the dropdown menu.

    command: dict
        Contains the type and data from a command sent by the HTML.
    """

    # NOTE: If more templates/command types are made, they must be entered in here.
    if command["action"] == 'home':
        template_name='home.html'
    elif command["action"] == 'designs':
        template_name='designs.html'
    elif command["action"] == 'input':
        template_name='input.html'
    else:
        template_name='home.html'

    # Compile values to be combined with the template.
    context = {
        'fields': command['src'],
        'dropdowns': dropdown
    }

    with open(abs_path('data/displayed_page.html'), 'w') as displayed_page:
        next_displayed_page = env.get_template(template_name).render(context)
        displayed_page.write(next_displayed_page)
