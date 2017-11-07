#Author-AIDE GUI
#Description-
import adsk.core, adsk.fusion, adsk.cam, traceback
import json
#import tkinter as tk

# Command inputs
_imgInputEnglish = adsk.core.ImageCommandInput.cast(None)
_imgInputMetric = adsk.core.ImageCommandInput.cast(None)

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
        
        # Create a command definition and add a button to the CREATE panel.
        cmdDef = ui.commandDefinitions.addButtonDefinition('adskAIDEPythonAddIn', 'AIDE', 'Creates Unit Process Designs', 'resources/aide_gui')        
        createPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        AIDE_Button = createPanel.controls.addCommand(cmdDef)
        
        if context['IsApplicationStartup'] == False:
            ui.messageBox('The "Spur Gear" command has been added\nto the CREATE panel of the MODEL workspace.')
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('Stop addin')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            
#def getCommandInputValue(commandInput, unitType):

