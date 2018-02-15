# Author-AIDE GUI

import adsk.core, adsk.fusion, adsk.cam, traceback
import json
import math


# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''


_errMessage = adsk.core.TextBoxCommandInput.cast(None)


# Event handlers
_handlers = []


# file_path= "/Users/eldorbekpualtov/Desktop/AguaClara/aide_gui/scratch_gui/test_gui/new_form.json"
# sys.path.append("/Users/eldorbekpualtov/anaconda3/lib/python3.6/site-packages")


# returns a correct abs path for a file
# def abs_path(file_path):
#     return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), file_path)

# parses json and for each key; creates a global in format: _[pName]
# always add absolute path to the json file
def createGLOBAL():
    # with open(file_path, 'r') as json_file:

    d='[{"flow_rate": [{"name": "Flow Rate (L/s)"}]}, {"sed_tank_length": [{"name": "Sed tank length (m)"}]}, {"blablabla": [{"name": "Hi There!"}]}]'
    data= json.loads(d)
    for param in data:
        pName = list(param.keys())[0]
        globals()['_%s' % pName] = adsk.core.StringValueCommandInput.cast(None)
    return data


def run(context):
    try:
        global _app, _ui
        # creates globals based on json
        # createGLOBAL()

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

############################
            flowRate = "24"
            # flowRateAttrib = des.attributes.itemByName('unit_design', 'flowRate')
            # if flowRateAttrib:
            #     flowRate = flowRateAttrib.value
            # d='[{"flow_rate": [{"name": "Flow Rate (L/s)"}]}, {"sed_tank_length": [{"name": "Sed tank length (m)"}]}, {"blablabla": [{"name": "Hi There!"}]}]'
            # data= json.loads(d)
            # for param in data:
            #     pName = list(param.keys())[0]
            #     globals()['_%s' % pName] = adsk.core.StringValueCommandInput.cast(None)
            # gl=globals()

            # Defining global parameters
            # global _flow_rate
            _flow_rate=adsk.core.StringValueCommandInput.cast(None)
            _flow_rate= inputs.addStringValueInput('flowRate', 'Flow Rate (L/s)', flowRate)
##############################

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
