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

def abs_path(file_path):
    # Takes a relative file path to the calling file and returns the correct
    # absolute path.
    # Needed because the Fusion 360 environment doesn't resolve relative paths
    # well.
    return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), file_path)

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)

# Create a yaml form structure in global called data
with open(abs_path("new_form.yaml")) as fp:
    data = yaml.load(fp)

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
        onCommandCreated = CommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        # Cleans up the UI once the add-in is stopped
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        AIDE_Button = createPanel.controls.itemById('adskaide_guiPythonAddIn')
        if AIDE_Button:
            AIDE_Button.deleteMe()

        cmdDef = _ui.commandDefinitions.itemById('adskaide_guiPythonAddIn')
        if cmdDef:
            cmdDef.deleteMe()

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

class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

            # Verify that a Fusion design is active.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            if not des:
                _ui.messageBox('A Fusion design must be active when invoked.')
                return()

            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Connect to the command destroyed event.
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # Create the globals based on attributes
            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs
            createFields(inputs)

            # to validate later just leave it for now
            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True

            # Connect to the command related events.
            onExecute = CommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            # Get the list of parameters and values from collectFields
            param_values = collectFields()
            # Create a new YAML file with parameters and values solicited
            # from the user
            with open(abs_path("collected.yaml"), 'w') as outfile:
                yaml.dump(param_values, outfile)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Creates fields to be displayed in a new window on Fusion 360 based on
# parameter list in input YAML to solicit parameter values from a user
def createFields(inputs):
    # Create a global list called plist to keep track of created fields
    globals()['plist'] = []
    # For each parameter {dictionary} in design param list
    for param in data:
        # Save the key of the first element as pName
        pName = list(param.keys())[0]
        # Get the value [attributes of field] of the key from the dictionary
        pAttr = param[pName]
        # Append the created global field to the plist (parameter list)
        plist.append(pName)
        # For fields specified by attr type: "string"
        if pAttr["type"] == "string":
            # param_format(id, name, default)
            globals()[pName] = inputs.addStringValueInput(str(pName), pAttr["name"], str(pAttr["default"]))
        # For fields specified by attr type: "dropdown"
        elif pAttr["type"] == "dropdown":
            # param_format(id, name, Dropdown)
            globals()[pName] = inputs.addDropDownCommandInput(str(pName), pAttr["name"], adsk.core.DropDownStyles.TextListDropDownStyle)
            # For each element in the list of options
            for option in pAttr["options"]:
                # Append the dropdown option values from input YAML
                globals()[pName].listItems.add(str(option), True)
        # For fields specified by attr type: "spinnerInt"
        elif pAttr["type"] == "spinnerInt":
            # param _format(id, Name, min, max, step, default)
            globals()[pName] = inputs.addIntegerSpinnerCommandInput(str(pName), pAttr["name"], pAttr["options"][0], pAttr["options"][2], pAttr["options"][1], pAttr["options"][0])
        # For fields specified by attr type: "spinnerFloat"
        elif pAttr["type"] == "spinnerFloat":
            # param _format(id, Name, min, max, step, default)
            globals()[pName] = inputs.addFloatSpinnerCommandInput(str(pName), pAttr["name"], '', pAttr["options"][0], pAttr["options"][2], pAttr["options"][1], pAttr["options"][0])

# Collect inputted values from the user and adds information to a list of
# dictionaries, each containing a parameter name and value
def collectFields():
    # Create a list of parameters from the parameter list
    parameters = []
    for key in plist:
        # If the parameter has a drop down type, the value is the selectedItem
        if isinstance(globals()[key], adsk.core.DropDownCommandInput):
            value = globals()[key].selectedItem.name
        # Otherwise it is simply the value the user enters
        else:
            value = globals()[key].value
        dictionary = {key: value}
        parameters.append(dictionary)
    return parameters
