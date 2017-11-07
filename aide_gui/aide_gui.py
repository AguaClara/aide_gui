#Author-AIDE GUI
#Description-
import adsk.core, adsk.fusion, adsk.cam, traceback
import json

# Command inputs
_imgInputEnglish = adsk.core.ImageCommandInput.cast(None)
_imgInputMetric = adsk.core.ImageCommandInput.cast(None)

# Global list to keep all event handlers in scope.
# This is only needed with Python.
handlers = []

#parse JSON from aide_design
def parseJsonObject(parameterJson):
    list = []
    try:
        list = json.loads(parameterJson)
    except ValueError:
        print("Decoding Json has failed")
    return list

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        s = json.dumps(["p1", "p2"])
        obj = parseJsonObject(s)
        #ui.messageBox('Hello addin')
    
        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions
        
        # Create a command definition
        cmdDef = cmdDefs.addButtonDefinition('adskaide_guiPythonAddIn', 'aide_gui', 'Creates Water Treatment Plant', './resources/AIDE')        
        
        # Get the Create Panel in the model workspace
        createPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        
        # Add the button to the bottom of the Create Panel
        AIDE_Button = createPanel.controls.addCommand(cmdDef)
        
        # Connect to the command created event.. functions to be written
        #onCommandCreated = CommandCreatedEventHandler()
        #AIDE_Button.commandCreated.add(onCommandCreated)
        #handlers.append(CommandCreated)
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        #ui.messageBox('Stop addin')
        
        # Cleans up the UI once add-in stopped        
        cmdDef = ui.commandDefinitions.itemById('adskaide_guiPythonAddIn')
        if cmdDef:
            cmdDef.deleteMe()
            
        createPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        AIDE_Button = createPanel.controls.itemById('adskaide_guiPythonAddIn')       
        if AIDE_Button:
            AIDE_Button.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            
            
