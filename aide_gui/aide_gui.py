# Author-AIDE GUI

import adsk.core, adsk.fusion, adsk.cam, traceback
import json
# import yaml
import math

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)  =
_units = ''

# Global list to keep all event handlers in scope (Currently hard-coded)
# This is only needed with Python.
_imgInputEnglish = adsk.core.ImageCommandInput.cast(None)
_imgInputMetric = adsk.core.ImageCommandInput.cast(None)
_standard = adsk.core.DropDownCommandInput.cast(None)
_errMessage = adsk.core.TextBoxCommandInput.cast(None)

_pressureAngle = adsk.core.DropDownCommandInput.cast(None)
_pressureAngleCustom = adsk.core.ValueCommandInput.cast(None)
_backlash = adsk.core.ValueCommandInput.cast(None)
_diaPitch = adsk.core.ValueCommandInput.cast(None)
_module = adsk.core.ValueCommandInput.cast(None)
_numTeeth = adsk.core.StringValueCommandInput.cast(None)
_rootFilletRad = adsk.core.ValueCommandInput.cast(None)
_thickness = adsk.core.ValueCommandInput.cast(None)
_holeDiam = adsk.core.ValueCommandInput.cast(None)
_pitchDiam = adsk.core.TextBoxCommandInput.cast(None)

# Event handlers
_handlers = []

<<<<<<< HEAD
=======

>>>>>>> 804ab9e4fc40912b08bae952e8bbe525bac636dd
# parse JSON from aide_design
def parseJsonObject(parameterJson):
    list = []
    try:
        list = json.loads(parameterJson)
    except ValueError:
        print("Decoding JSON has failed")
    return list


def run(context):
    try:
        global _app, _ui
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

            defaultUnits = des.unitsManager.defaultLengthUnits

            # Determine whether to use inches or millimeters as the default unit
            global _units
            if defaultUnits == 'in' or defaultUnits == 'ft':
                _units = 'in'
            else:
                _units = 'mm'

            # Define the default values and get the previous values from the attributes.
            if _units == 'in':
                standard = 'English'
            else:
                standard = 'Metric'
            standardAttrib = des.attributes.itemByName('unit_design', 'standard') # design name, attribute
            if standardAttrib:
                standard = standardAttrib.value

            if standard == 'English':
                _units = 'in'
            else:
                _units = 'mm'

            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Connect to the command destroyed event.
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

#            Connect to the input changed event.  (Needed when more input event handlers created later)
#            onInputChanged = MyCommandInputChangedHandler()
#            cmd.inputChanged.add(onInputChanged)
#            _handlers.append(onInputChanged)

#            # Get the CommandInputs collection associated with the command.
#            inputs = cmd.commandInputs
#
             # (Optional) Can implement tabs for different unit process designs if needed
#            # Create a tab input.
#            tabCmdInput1 = inputs.addTabCommandInput('tab_1', 'Tab 1')
#            tab1ChildInputs = tabCmdInput1.children
#
#            # Create value input.
#            tab1ChildInputs.addValueInput('value', 'Value', 'cm', adsk.core.ValueInput.createByReal(0.0))
#
#            # Create tab input 2
#            tabCmdInput2 = inputs.addTabCommandInput('tab_2', 'Tab 2')
#            tab2ChildInputs = tabCmdInput2.children
#
#             # Create value input.
#            tab2ChildInputs.addValueInput('value', 'Value', 'cm', adsk.core.ValueInput.createByReal(0.0))

            # Hard coded inputs, text input

            pressureAngle = '20 deg'
            pressureAngleAttrib = des.attributes.itemByName('unit_design', 'pressureAngle') # design name, parameter
            if pressureAngleAttrib:
                pressureAngle = pressureAngleAttrib.value

            pressureAngleCustom = 20 * (math.pi/180.0)
            pressureAngleCustomAttrib = des.attributes.itemByName('unit_design', 'pressureAngleCustom')
            if pressureAngleCustomAttrib:
                pressureAngleCustom = float(pressureAngleCustomAttrib.value)

            diaPitch = '2'
            diaPitchAttrib = des.attributes.itemByName('unit_design', 'diaPitch')
            if diaPitchAttrib:
                diaPitch = diaPitchAttrib.value
            metricModule = 25.4 / float(diaPitch)

            backlash = '0'
            backlashAttrib = des.attributes.itemByName('unit_design', 'backlash')
            if backlashAttrib:
                backlash = backlashAttrib.value

            numTeeth = '24'
            numTeethAttrib = des.attributes.itemByName('unit_design', 'numTeeth')
            if numTeethAttrib:
                numTeeth = numTeethAttrib.value

            rootFilletRad = str(.0625 * 2.54)
            rootFilletRadAttrib = des.attributes.itemByName('unit_design', 'rootFilletRad')
            if rootFilletRadAttrib:
                rootFilletRad = rootFilletRadAttrib.value

            thickness = str(0.5 * 2.54)
            thicknessAttrib = des.attributes.itemByName('unit_design', 'thickness')
            if thicknessAttrib:
                thickness = thicknessAttrib.value

            holeDiam = str(0.5 * 2.54)
            holeDiamAttrib = des.attributes.itemByName('unit_design', 'holeDiam')
            if holeDiamAttrib:
                holeDiam = holeDiamAttrib.value

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs

            # Defining global parameters

            global _standard, _pressureAngle, _pressureAngleCustom, _diaPitch, _pitch, _module, _numTeeth, _rootFilletRad, _thickness, _holeDiam, _pitchDiam, _backlash, _imgInputEnglish, _imgInputMetric, _errMessage

            # Drop-down inputs, optional for some parameters with fixed range of values

            _standard = inputs.addDropDownCommandInput('standard', 'Standard', adsk.core.DropDownStyles.TextListDropDownStyle)
            if standard == "English":
                _standard.listItems.add('English', True)
                _standard.listItems.add('Metric', False)

            else:
                _standard.listItems.add('English', False)
                _standard.listItems.add('Metric', True)

            _pressureAngle = inputs.addDropDownCommandInput('pressureAngle', 'Pressure Angle', adsk.core.DropDownStyles.TextListDropDownStyle)
            if pressureAngle == '14.5 deg':
                _pressureAngle.listItems.add('14.5 deg', True)
            else:
                _pressureAngle.listItems.add('14.5 deg', False)

            if pressureAngle == '20 deg':
                _pressureAngle.listItems.add('20 deg', True)
            else:
                _pressureAngle.listItems.add('20 deg', False)

            if pressureAngle == '25 deg':
                _pressureAngle.listItems.add('25 deg', True)
            else:
                _pressureAngle.listItems.add('25 deg', False)

            if pressureAngle == 'Custom':
                _pressureAngle.listItems.add('Custom', True)
            else:
                _pressureAngle.listItems.add('Custom', False)

            _pressureAngleCustom = inputs.addValueInput('pressureAngleCustom', 'Custom Angle', 'deg', adsk.core.ValueInput.createByReal(pressureAngleCustom))
            if pressureAngle != 'Custom':
                _pressureAngleCustom.isVisible = False

            _diaPitch = inputs.addValueInput('diaPitch', 'Diametral Pitch', '', adsk.core.ValueInput.createByString(diaPitch))

            _module = inputs.addValueInput('module', 'Module', '', adsk.core.ValueInput.createByReal(metricModule))

            if standard == 'English':
                _module.isVisible = False
            elif standard == 'Metric':
                _diaPitch.isVisible = False

            # The initial values of the inputs as shown in the dialog

            _numTeeth = inputs.addStringValueInput('numTeeth', 'Number of Teeth', numTeeth)

            _backlash = inputs.addValueInput('backlash', 'Backlash', _units, adsk.core.ValueInput.createByReal(float(backlash)))

            _rootFilletRad = inputs.addValueInput('rootFilletRad', 'Root Fillet Radius', _units, adsk.core.ValueInput.createByReal(float(rootFilletRad)))

            _thickness = inputs.addValueInput('thickness', 'Gear Thickness', _units, adsk.core.ValueInput.createByReal(float(thickness)))

            _holeDiam = inputs.addValueInput('holeDiam', 'Hole Diameter', _units, adsk.core.ValueInput.createByReal(float(holeDiam)))

            _pitchDiam = inputs.addTextBoxCommandInput('pitchDiam', 'Pitch Diameter', '', 1, True)

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
