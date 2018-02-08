# Author-Eldor
# Description-For learning purposes of Eldor only! Please do not modify!

import adsk.core
import adsk.fusion
import adsk.cam
import traceback

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''


def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = app.userInterface

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

        if context['IsApplicationStartup'] == False:
            _ui.messageBox('The "AIDE" has been added to the CREATE panel.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox('Stop addin')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
