# Author-AIDE GUI

import adsk.core, adsk.fusion, adsk.cam, traceback
import json
# import yaml
import math
import os

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''

# _numTeeth = adsk.core.StringValueCommandInput.cast(None)

# Event handlers
_handlers = []

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

def run(context):
    try:
        global _app, _ui
        createGLOBAL()
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = _ui.commandDefinitions

        # Create a command definition
        cmdDef = cmdDefs.addButtonDefinition('adskaide_guiPythonAddIn', 'aide_gui', 'Creates Water Treatment Plant', './resources/AIDE')

        # Get the Create Panel in the model workspace
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')

        # Add the button to the bottom of the Create Panel
        AIDE_Button = createPanel.controls.addCommand(cmdDef)

        # Connect to the command created event (functions to be written)
        onCommandCreated = CommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        _ui.messageBox('Current working directory: \"{}\"'.format(os.getcwd()))

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

            defaultUnits = des.unitsManager.defaultLengthUnits

            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Connect to the command destroyed event.
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # The initial values of the inputs as shown in the dialog

            _numTeeth = inputs.addStringValueInput('numTeeth', 'Number of Teeth', numTeeth)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
