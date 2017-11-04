#Author-AIDE GUI
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
import json

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
        ui.messageBox('Hello addin')

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
