import os, sys, inspect, json, math
import adsk.core, adsk.fusion, adsk.cam, traceback, datetime

# returns absolute path
def abs_path(file_path):
    return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), file_path)

# add the path to local library
sys.path.append(abs_path('.'))

from . import yaml
from . import urllib3
from .jinja2 import Template, Environment, FileSystemLoader, select_autoescape
from .helper import jinjafy, render, load_yaml


link_cards = 'https://raw.githubusercontent.com/AguaClara/aide_gui/spring-2018/palette_docs/home/cards.yaml'
link_dropdown ='https://raw.githubusercontent.com/AguaClara/aide_gui/spring-2018/palette_docs/home/dropdown.yaml'
# this is loaded here because we want to fetch dropdown once only
dropdown=load_yaml(link_dropdown)


# global set of event handlers to keep them referenced for the duration of the command
handlers = []
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_environment = Environment(
    loader=FileSystemLoader(abs_path('.')+'/templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


# Event handler for the commandCreated event.
class ShowPaletteCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            command = args.command
            onExecute = ShowPaletteCommandExecuteHandler()
            command.execute.add(onExecute)
            handlers.append(onExecute)
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the commandExecuted event.
class ShowPaletteCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global _ui, _app, _environment
            # Create or display the palette.
            palette = _ui.palettes.itemById('myPalette')
            if not palette:

                command={
                    'type' : 'home',
                    'link' : link_cards
                }
                # if there was no palette then open homepage
                jinjafy(_environment, dropdown, command)

                # let palette open the jinjafied.html
                palette = _ui.palettes.add('myPalette', 'My Palette', 'jinjafied.html', True, True, True, 300, 200)
                palette.setMinimumSize(300, 400)
                # palette.setMaximumSize(300, 400)

                # Dock the palette to the right side of Fusion window.
                palette.dockingState = adsk.core.PaletteDockingStates.PaletteDockStateRight

                # Add handler to HTMLEvent of the palette.
                onHTMLEvent = MyHTMLEventHandler()
                palette.incomingFromHTML.add(onHTMLEvent)
                handlers.append(onHTMLEvent)

            else:
                palette.isVisible = True
        except:
            _ui.messageBox('Command executed failed: {}'.format(traceback.format_exc()))

# Event handler for the palette HTML event.
class MyHTMLEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            htmlArgs = adsk.core.HTMLEventArgs.cast(args)
            incoming = json.loads(htmlArgs.data)
            # data is what is being sent from pallete in json form

            palette = _ui.palettes.itemById('myPalette')
            jinjafy(_environment, dropdown, incoming)
            # Set the html of the palette.
            palette.htmlFileURL = 'jinjafied.html'

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



# Event handler for the commandCreated event.
class SendInfoCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            command = args.command
            onExecute = SendInfoCommandExecuteHandler()
            command.execute.add(onExecute)
            handlers.append(onExecute)
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the commandExecuted event.
class SendInfoCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # Send information to the palette.
            palette = _ui.palettes.itemById('myPalette')
            if palette:
                # here we replaced some terms so JSON in js recognizes the form
                palette.sendInfoToHTML('send', str(data).replace("'", '"').replace("None", 'null'))
        except:
            _ui.messageBox('Command executed failed: {}'.format(traceback.format_exc()))



def run(context):
    try:
        global _ui, _app, _environment
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        # Add a command that displays the panel.
        showPaletteCmdDef = _ui.commandDefinitions.itemById('showPalette')
        if not showPaletteCmdDef:
            showPaletteCmdDef = _ui.commandDefinitions.addButtonDefinition('showPalette', 'Show Palette', 'Show AIDE palette', '')

            # Connect to Command Created event.
            onCommandCreated = ShowPaletteCommandCreatedHandler()
            showPaletteCmdDef.commandCreated.add(onCommandCreated)
            handlers.append(onCommandCreated)


        # Add a command under ADD-INS panel which sends information from Fusion to the palette's HTML.
        sendInfoCmdDef = _ui.commandDefinitions.itemById('sendInfoToHTML')
        if not sendInfoCmdDef:
            sendInfoCmdDef = _ui.commandDefinitions.addButtonDefinition('sendInfoToHTML', 'Send info to Palette', 'Send Info to Palette HTML', '')

            # Connect to Command Created event.
            onCommandCreated = SendInfoCommandCreatedHandler()
            sendInfoCmdDef.commandCreated.add(onCommandCreated)
            handlers.append(onCommandCreated)


        # Get the Create Panel in the model workspace in Fusion
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        # Add the button to the bottom of the Create Panel in Fusion
        showPaletteButton= createPanel.controls.addCommand(showPaletteCmdDef)
        sendInfoButton= createPanel.controls.addCommand(sendInfoCmdDef)

        # open the pallete as soon as user presses run()
        showPaletteCmdDef.execute()

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        # Delete the palette created by this add-in.
        palette = _ui.palettes.itemById('myPalette')
        if palette:
            palette.deleteMe()

        # Delete the created buttons under SolidCreatePanel
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')

        showPaletteButton = createPanel.controls.itemById('showPalette')
        if showPaletteButton:
            showPaletteButton.deleteMe()

        sendInfoButton = createPanel.controls.itemById('sendInfoToHTML')
        if sendInfoButton:
            sendInfoButton.deleteMe()

        # Delete controls and associated command definitions created by this add-ins
        cmdDef = _ui.commandDefinitions.itemById('showPalette')
        if cmdDef:
            cmdDef.deleteMe()

        cmdDef = _ui.commandDefinitions.itemById('sendInfoToHTML')
        if cmdDef:
            cmdDef.deleteMe()

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CommandExecuteHandler(adsk.core.CommandEventHandler):
    """
    Creates a new YAML based on user inputs and the list of fields to be
    collected
    Parameters
    ----------
    fields: dict
        The design parameter list as a dictionary from the user inputted YAML
    """
    def __init__(self, fields):
        super().__init__()
        self.fields = fields

    def notify(self, args):
        try:
        # Get the list of parameters and values from collectFields
            param_values = collectFields(self.fields)

        current_time = str(datetime.datetime.now())
        # output a file with collected values
         with open(abs_path("user_inputs_"+ current_time + ".yaml"), 'w') as outfile:
             yaml.dump(param_values, outfile)

        # Execute on finish code here (call aide_design/aide_templates)
        except:
                if _ui:
                    _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


    def load_yaml(files_path):
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
            with open(abs_path(file_path)) as fp:
                    yam = yaml.load(fp)
            if (type(yam) != list and type(yam) != dict):
                raise Exception('This is not a YAML')
                return  yam
            except:
        # If yaml is retrieved from a given url
                try:
                    url = file_path.strip()
                    http = urllib3.PoolManager()
                    r = http.request('GET', url)
                    status = r.status # check URL status
                    if (status != 200):
                        raise Exception('This is not a URL')
                        yam =  yaml.load(r.data.decode('utf-8'))
                        return yam
                    except:
                        if _ui:
                            _ui.messageBox('Not a YAML or URL \nPlease provide a correct form.')
                            return None


    def createFields(inputs, yaml_form):
    """
    Creates fields to be displayed in a new window on Fusion 360 based on
    parameter list in input YAML to solicit parameter values from a user
    Parameters
    ----------
    inputs: CommandInputs
        The collection of command inputs
    yaml_form: list
        The design parameter list from the user inputted YAML
    Return
    --------
    fields: dict
        A dictionary to keep track of created fields
    """
        fields = {}
    # For each parameter {dictionary} in design param list
        for param in yaml_form:
        # Save the key of the first element as pName
                pName = list(param.keys())[0]
        # Get the value [attributes of field] of the key from the dictionary
                pAttr = param[pName]
        # For fields specified by attr type: "string"
                if pAttr["type"] == "string":
            # param_format(id, name, default)
                    fields[pName]= inputs.addStringValueInput(str(pName), pAttr["name"], str(pAttr["default"]))
        # For fields specified by attr type: "dropdown"
                elif pAttr["type"] == "dropdown":
            # param_format(id, name, Dropdown)
                    fields[pName]= inputs.addDropDownCommandInput(str(pName), pAttr["name"], adsk.core.DropDownStyles.TextListDropDownStyle)
            # For each element in the list of options
            for option in pAttr["options"]:
                # Append the dropdown option values from input YAML
                    fields[pName].listItems.add(str(option), True)
        # For fields specified by attr type: "spinnerInt"
                elif pAttr["type"] == "spinnerInt":
            # param _format(id, Name, min, max, step, default)
                    fields[pName] = inputs.addIntegerSpinnerCommandInput(str(pName), pAttr["name"], pAttr["options"][0], pAttr["options"][2], pAttr["options"][1], pAttr["options"][0])
        # For fields specified by attr type: "spinnerFloat"
                elif pAttr["type"] == "spinnerFloat":
            # param _format(id, Name, min, max, step, default)
                    fields[pName] = inputs.addFloatSpinnerCommandInput(str(pName), pAttr["name"], '', pAttr["options"][0], pAttr["options"][2], pAttr["options"][1], pAttr["options"][0])

                    return fields


    def collectFields(fields):
    """
    Collect inputted values from the user and adds information to a list of
    dictionaries, each containing a parameter name and value
    Parameters
    ----------
    fields: list
        The list of created field IDs from createFields
    Return
    ----------
    params: dict
        A dictionary with the design parameter name as keys and the user
        inputted values as values
    """
        params = {}
        for key, kval in fields.items():
        # If the parameter has a drop down type, the value is the selectedItem
            if isinstance(kval, adsk.core.DropDownCommandInput):
                value = kval.selectedItem.name
        # Otherwise it is simply the value the user enters
            else:
                value = kval.value
                params[key]=value
                return params
