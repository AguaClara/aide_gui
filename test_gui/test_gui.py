# Author-AIDE GUI
import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import json
import math
import os
import sys
import inspect
from . import yaml
from . import urllib3
import datetime

def abs_path(file_path):
    """
    Takes a relative file path to the calling file and returns the correct
    absolute path. Needed because the Fusion 360 environment doesn't resolve
    relative paths well.

    Parameters
    ----------
    file_path: str
        Relative file path to the calling file
    """
    return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), file_path)

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)


# Error Message
_errMessage = adsk.core.TextBoxCommandInput.cast(None)

# Global list to keep all event handlers in scope
_handlers = []

def run(context):
    """
    Creates the command definition, adds button to the bottom of the Create
    Panel in Fusion, and connects to the command created event.
    """
    try:
        global _app, _ui

        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = _ui.commandDefinitions

        # Create a command definition
        cmdDef = cmdDefs.addButtonDefinition('adskaide_guiPythonAddIn',
            'AIDE GUI', 'Creates Water Treatment Plant', './resources/AIDE')

        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        AIDE_Button = createPanel.controls.addCommand(cmdDef)

        onCommandPath = CommandPathHandler()
        cmdDef.commandCreated.add(onCommandPath)
        _handlers.append(onCommandPath)

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    """
    Cleans up the UI once the add-in is stopped.
    """
    try:
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        AIDE_Button = createPanel.controls.itemById('adskaide_guiPythonAddIn')

        cmdDef = _ui.commandDefinitions.itemById('adskaide_guiPythonAddIn')
        cmdDef1 = _ui.commandDefinitions.itemById('loadFormat')

        if AIDE_Button:
            AIDE_Button.deleteMe()
        if cmdDef:
            cmdDef.deleteMe()
        if cmdDef1:
            cmdDef1.deleteMe()

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    """
    When the command is done, terminate the add-in. This will release all
    globals and remove all event handlers.
    """
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            adsk.terminate()

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class CommandPathHandler(adsk.core.CommandCreatedEventHandler):
    """
    Uses the CommandCreatedEventHandler to create a window to request yaml local
    path or url from User.
    """
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs

            # Ask for user to specify filepath
            globals()['file_path'] = inputs.addStringValueInput('path', "File Path/URL", '')

            # Connect to the command related events.
            onPathLoad = PathLoadHandler()
            cmd.execute.add(onPathLoad)
            _handlers.append(onPathLoad)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class PathLoadHandler(adsk.core.CommandEventHandler):
    """
    Handles when user inputs file path/URL and hits 'OK'
    """
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            yam = load_yaml(globals()["file_path"].value)
            if  yam != None:
                # Get the CommandDefinitions collection.
                cmdDefs = _ui.commandDefinitions

                # Create a button command definition
                loadButton = cmdDefs.addButtonDefinition('loadFormat',
                        'Template','Creates template to collect user parameters')

                # Connect to the command created event to create the window
                onCommandCreated = CommandCreatedHandler(yam)
                loadButton.commandCreated.add(onCommandCreated)
                _handlers.append(onCommandCreated)

                # Execute the command.
                loadButton.execute()
            else:
                # if the user specified bad path: notify then repress the button automatically
                cmdDef = _ui.commandDefinitions.itemById('adskaide_guiPythonAddIn')
                cmdDef.execute()

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """
    Creates the second window after retrieving parameters from an inputted yaml.

    Parameters
    ----------
    yaml_form: list
        The design parameter list from the user inputted YAML
    """
    def __init__(self, yaml_form):
        super().__init__()
        self.yaml_form = yaml_form

    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            # Create the globals based on attributes
            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs
            # Connect to the command destroyed event.
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # This creates the fields given that format file has succesfully loaded
            fields = createFields(inputs, self.yaml_form)

            # Connect to the command related events.
            onExecute = CommandExecuteHandler(fields)
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)

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
