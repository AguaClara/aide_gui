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

def abs_path(file_path):
    # Takes a relative file path to the calling file and returns the correct
    # absolute path.
    # Needed because the Fusion 360 environment doesn't resolve relative paths
    # well.
    return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), file_path)

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)


# Error Message
_errMessage = adsk.core.TextBoxCommandInput.cast(None)

# Event handlers
_handlers = []

def run(context):
    try:
        global _app, _ui

        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = _ui.commandDefinitions

        # Create a command definition
        cmdDef = cmdDefs.addButtonDefinition('adskaide_guiPythonAddIn',
            'AIDE GUI', 'Creates Water Treatment Plant', './resources/AIDE')

        # Get the Create Panel in the model workspace in Fusion
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')

        # Add the button to the bottom of the Create Panel in Fusion
        AIDE_Button = createPanel.controls.addCommand(cmdDef)

        # Connect to the command created event (functions to be written)
        onCommandPath = CommandPathHandler()
        cmdDef.commandCreated.add(onCommandPath)
        _handlers.append(onCommandPath)


    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        # Cleans up the UI once the add-in is stopped
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
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            # When the command is done, terminate the add-in
            # This will release all globals and remove all event handlers
            adsk.terminate()

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Creates a window to request yaml local path or url from user
class CommandPathHandler(adsk.core.CommandCreatedEventHandler):
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
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            # Get the file path from user
            fpath = globals()['file_path'].value

            if load_yaml(fpath) != None:
                # Get the CommandDefinitions collection.
                cmdDefs = _ui.commandDefinitions

                # Create a button command definition
                loadButton = cmdDefs.addButtonDefinition('loadFormat',
                        'Template','Creates template to collect user parameters')

                # Connect to the command created event to create the window
                onCommandCreated = CommandCreatedHandler()
                loadButton.commandCreated.add(onCommandCreated)
                _handlers.append(onCommandCreated)

                # Execute the command.
                loadButton.execute()

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Creates the second window after retrieving parameters from inputted yaml
class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

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

            # this creates the fields given that format file has succesfully loaded
            fields = createFields(inputs)

            # Connect to the command related events.
            onExecute = CommandExecuteHandler(fields)
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Create a new window with parameters from loaded YAML
class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self, fields):
        super().__init__()
        self.fields = fields

    def notify(self, args):
        try:
            # Get the list of parameters and values from collectFields
            param_values = collectFields(self.fields)

            # output a file with collected values
            with open(abs_path("collected.yaml"), 'w') as outfile:
                yaml.dump(param_values, outfile)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Create a yaml form structure in global called data
def load_yaml(fpath):
    # If yaml is retrieved from user's local path
    try:
        with open(abs_path(fpath)) as fp:
            v = yaml.load(fp)
            if (type(v) != list and type(v) != dict):
                raise Exception('This is not a YAML')
            globals()['yaml_form'] = v
            return  yaml
    except:
        # If yaml is retrieved from a given url
        try:
            url = fpath.strip()
            http = urllib3.PoolManager()
            r = http.request('GET', url)
            status = r.status # check URL status
            if (status != 200):
                raise Exception('This is not a URL')
            globals()['yaml_form'] =  yaml.load(r.data.decode('utf-8'))
            return yaml
        except:
            if _ui:
                _ui.messageBox('Not a YAML or URL \nPlease provide a correct form.')
            return None


# Creates fields to be displayed in a new window on Fusion 360 based on
# parameter list in input YAML to solicit parameter values from a user
def createFields(inputs):
    # Create a global list called plist to keep track of created fields

    fields = {}
    # For each parameter {dictionary} in design param list
    for param in globals()['yaml_form']:
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

    # returns the list of created field ids
    return fields

# Collect inputted values from the user and adds information to a list of
# dictionaries, each containing a parameter name and value
def collectFields(fields):
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
