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
    """
    Takes a relative file path to the calling file and returns the correct
    absolute path.
    Needed because the Fusion 360 environment doesn't resolve relative paths
    well.
    """
    return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), file_path)

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''

# create a yaml form structure in global called data
with open(abs_path("new_form.yaml")) as fp:
    data = yaml.load(fp)

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
        cmdDef = cmdDefs.addButtonDefinition('adskaide_guiPythonAddIn', 'Scratch GUI', 'Creates Water Treatment Plant', './resources/AIDE')

        # Get the Create Panel in the model workspace
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')

        # Add the button to the bottom of the Create Panel
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
        # Cleans up the UI once add-in stopped
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
                _ui.messageBox('A Fusion design must be active when invoking this command.')
                return()

            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Connect to the command destroyed event.
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs

            ##############################
            # create the globals based on attributes
            ##############################
            globals()['plist'] = []
            for param in data:
                pName = list(param.keys())[0]
                pAttr = param[pName]
                # get the list of added globals
                plist.append(pName)
                if pAttr["type"] == "string":
                    globals()[pName] = inputs.addStringValueInput(str(pName), pAttr["name"], str(pAttr["default"]))
                elif pAttr["type"] == "dropdown":
                    globals()[pName] = inputs.addDropDownCommandInput(str(pName), pAttr["name"], adsk.core.DropDownStyles.TextListDropDownStyle)
                    for option in pAttr["options"]:
                        globals()[pName].listItems.add(str(option), True)
                elif pAttr["type"] == "spinnerInt":
                    globals()[pName] = inputs.addIntegerSpinnerCommandInput(str(pName), pAttr["name"], pAttr["options"][0], pAttr["options"][2], pAttr["options"][1], pAttr["options"][0])
                elif pAttr["type"] == "spinnerFloat":
                    globals()[pName] = inputs.addFloatSpinnerCommandInput(str(pName), pAttr["name"], '', pAttr["options"][0], pAttr["options"][2], pAttr["options"][1], pAttr["options"][0])
            ##############################
            # get the value of each global input and saves it in global list
            ##############################
            globals()['parameters'] = []
            for p in plist:
                key = "_" + str(p)
                if isinstance(globals()[key], adsk.core.DropDownCommandInput):
                    value= globals()[key].selectedItem.name
                else:
                    value = globals()[key].value
                dictionary = {key: value}
                parameters.append(dictionary)
            _ui.messageBox(str(parameters))
            ###############################


            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True

            '''
            # Connect to the command related events. (Not used yet)
            onExecute = GearCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)

            onInputChanged = GearCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)

            onValidateInputs = GearCommandValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            _handlers.append(onValidateInputs)
            '''

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
