#Author-AIDE GUI
#Description-GUI for aide_design

import adsk.core, adsk.fusion, adsk.cam, traceback


# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''

# Command inputs
_imgInputEnglish = adsk.core.ImageCommandInput.cast(None)
_imgInputMetric = adsk.core.ImageCommandInput.cast(None)

_plantFlowRate = adsk.core.ValueCommandInput.cast(None)
_flocHeadLoss = adsk.core.ValueCommandInput.cast(None)
_flocBlanketDepth = adsk.core.ValueCommandInput.cast(None)
_flocSlabThickness = adsk.core.ValueCommandInput.cast(None)
_flocOuterWall = adsk.core.ValueCommandInput.cast(None)
_flocDividingWall = adsk.core.ValueCommandInput.cast(None)
_thickness = adsk.core.ValueCommandInput.cast(None)

_handlers = []

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('Hello addin')

        # Create a command definition and add a button to the CREATE panel.
        cmdDef = _ui.commandDefinitions.addButtonDefinition('adskAIDEPythonAddIn', 'AIDE', 'Creates Water Treatment Plant', 'Resources/AIDE')        
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        AIDEButton = createPanel.controls.addCommand(cmdDef)
        
        # Connect to the command created event.
        onCommandCreated = AIDECommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        
        if context['IsApplicationStartup'] == False:
            _ui.messageBox('The "AIDE Design Tool" has been added\nto the CREATE panel of the MODEL workspace.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
    createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
    AIDEButton = createPanel.controls.itemById('adskAIDEPythonAddIn')       
    if AIDEButton:
        AIDEButton.deleteMe()
        
    cmdDef = _ui.commandDefinitions.itemById('adskAIDEPythonAddIn')
    if cmdDef:
        cmdDef.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Verifies that a value command input has a valid expression and returns the 
# value if it does.  Otherwise it returns False.  This works around a 
# problem where when you get the value from a ValueCommandInput it causes the
# current expression to be evaluated and updates the display.  Some new functionality
# is being added in the future to the ValueCommandInput object that will make 
# this easier and should make this function obsolete.
def getCommandInputValue(commandInput, unitType):
    try:
        valCommandInput = adsk.core.ValueCommandInput.cast(commandInput)
        if not valCommandInput:
            return (False, 0)

        # Verify that the expression is valid.
        des = adsk.fusion.Design.cast(_app.activeProduct)
        unitsMgr = des.unitsManager
        
        if unitsMgr.isValidExpression(valCommandInput.expression, unitType):
            value = unitsMgr.evaluateExpression(valCommandInput.expression, unitType)
            return (True, value)
        else:
            return (False, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

"""# Event handler for the commandCreated event.
class GearCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
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
                
            # Determine whether to use inches or millimeters as the intial default.
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
            standardAttrib = des.attributes.itemByName('SpurGear', 'standard')
            if standardAttrib:
                standard = standardAttrib.value
                
            if standard == 'English':
                _units = 'in'
            else:
                _units = 'mm'
            
            pressureAngle = '20 deg'
            pressureAngleAttrib = des.attributes.itemByName('SpurGear', 'pressureAngle')
            if pressureAngleAttrib:
                pressureAngle = pressureAngleAttrib.value
            
            pressureAngleCustom = 20 * (math.pi/180.0)
            pressureAngleCustomAttrib = des.attributes.itemByName('SpurGear', 'pressureAngleCustom')
            if pressureAngleCustomAttrib:
                pressureAngleCustom = float(pressureAngleCustomAttrib.value)            

            diaPitch = '2'
            diaPitchAttrib = des.attributes.itemByName('SpurGear', 'diaPitch')
            if diaPitchAttrib:
                diaPitch = diaPitchAttrib.value
            metricModule = 25.4 / float(diaPitch)

            backlash = '0'
            backlashAttrib = des.attributes.itemByName('SpurGear', 'backlash')
            if backlashAttrib:
                backlash = backlashAttrib.value

            numTeeth = '24'            
            numTeethAttrib = des.attributes.itemByName('SpurGear', 'numTeeth')
            if numTeethAttrib:
                numTeeth = numTeethAttrib.value

            rootFilletRad = str(.0625 * 2.54)
            rootFilletRadAttrib = des.attributes.itemByName('SpurGear', 'rootFilletRad')
            if rootFilletRadAttrib:
                rootFilletRad = rootFilletRadAttrib.value

            thickness = str(0.5 * 2.54)
            thicknessAttrib = des.attributes.itemByName('SpurGear', 'thickness')
            if thicknessAttrib:
                thickness = thicknessAttrib.value
            
            holeDiam = str(0.5 * 2.54)
            holeDiamAttrib = des.attributes.itemByName('SpurGear', 'holeDiam')
            if holeDiamAttrib:
                holeDiam = holeDiamAttrib.value

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs
            
            global _standard, _pressureAngle, _pressureAngleCustom, _diaPitch, _pitch, _module, _numTeeth, _rootFilletRad, _thickness, _holeDiam, _pitchDiam, _backlash, _imgInputEnglish, _imgInputMetric, _errMessage

            # Define the command dialog.
            _imgInputEnglish = inputs.addImageCommandInput('gearImageEnglish', '', 'Resources/GearEnglish.png')
            _imgInputEnglish.isFullWidth = True

            _imgInputMetric = inputs.addImageCommandInput('gearImageMetric', '', 'Resources/GearMetric.png')
            _imgInputMetric.isFullWidth = True

            _standard = inputs.addDropDownCommandInput('standard', 'Standard', adsk.core.DropDownStyles.TextListDropDownStyle)
            if standard == "English":
                _standard.listItems.add('English', True)
                _standard.listItems.add('Metric', False)
                _imgInputMetric.isVisible = False
            else:
                _standard.listItems.add('English', False)
                _standard.listItems.add('Metric', True)
                _imgInputEnglish.isVisible = False            
            
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
                
            _numTeeth = inputs.addStringValueInput('numTeeth', 'Number of Teeth', numTeeth)        

            _backlash = inputs.addValueInput('backlash', 'Backlash', _units, adsk.core.ValueInput.createByReal(float(backlash)))

            _rootFilletRad = inputs.addValueInput('rootFilletRad', 'Root Fillet Radius', _units, adsk.core.ValueInput.createByReal(float(rootFilletRad)))

            _thickness = inputs.addValueInput('thickness', 'Gear Thickness', _units, adsk.core.ValueInput.createByReal(float(thickness)))

            _holeDiam = inputs.addValueInput('holeDiam', 'Hole Diameter', _units, adsk.core.ValueInput.createByReal(float(holeDiam)))

            _pitchDiam = inputs.addTextBoxCommandInput('pitchDiam', 'Pitch Diameter', '', 1, True)
            
            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True
            
            # Connect to the command related events.
            onExecute = GearCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)        
            
            onInputChanged = GearCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)     
            
            onValidateInputs = GearCommandValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            _handlers.append(onValidateInputs)        
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the execute event.
class GearCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            if _standard.selectedItem.name == 'English':
                diaPitch = _diaPitch.value            
            elif _standard.selectedItem.name == 'Metric':
                diaPitch = 25.4 / _module.value
            
            # Save the current values as attributes.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            attribs = des.attributes
            attribs.add('SpurGear', 'standard', _standard.selectedItem.name)
            attribs.add('SpurGear', 'pressureAngle', _pressureAngle.selectedItem.name)
            attribs.add('SpurGear', 'pressureAngleCustom', str(_pressureAngleCustom.value))
            attribs.add('SpurGear', 'diaPitch', str(diaPitch))
            attribs.add('SpurGear', 'numTeeth', str(_numTeeth.value))
            attribs.add('SpurGear', 'rootFilletRad', str(_rootFilletRad.value))
            attribs.add('SpurGear', 'thickness', str(_thickness.value))
            attribs.add('SpurGear', 'holeDiam', str(_holeDiam.value))
            attribs.add('SpurGear', 'backlash', str(_backlash.value))

            # Get the current values.
            if _pressureAngle.selectedItem.name == 'Custom':
                pressureAngle = _pressureAngleCustom.value
            else:
                if _pressureAngle.selectedItem.name == '14.5 deg':
                    pressureAngle = 14.5 * (math.pi/180)
                elif _pressureAngle.selectedItem.name == '20 deg':
                    pressureAngle = 20.0 * (math.pi/180)
                elif _pressureAngle.selectedItem.name == '25 deg':
                    pressureAngle = 25.0 * (math.pi/180)

            numTeeth = int(_numTeeth.value)
            rootFilletRad = _rootFilletRad.value
            thickness = _thickness.value
            holeDiam = _holeDiam.value
            backlash = _backlash.value

            # Create the gear.
            gearComp = drawGear(des, diaPitch, numTeeth, thickness, rootFilletRad, pressureAngle, backlash, holeDiam)
            
            if gearComp:
                if _standard.selectedItem.name == 'English':
                    desc = 'Spur Gear; Diametrial Pitch: ' + str(diaPitch) + '; '            
                elif _standard.selectedItem.name == 'Metric':
                    desc = 'Spur Gear; Module: ' +  str(25.4 / diaPitch) + '; '
                
                desc += 'Num Teeth: ' + str(numTeeth) + '; '
                desc += 'Pressure Angle: ' + str(pressureAngle * (180/math.pi)) + '; '
                
                desc += 'Backlash: ' + des.unitsManager.formatInternalValue(backlash, _units, True)
                gearComp.description = desc
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


        
# Event handler for the inputChanged event.
class GearCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input
            
            global _units
            if changedInput.id == 'standard':
                if _standard.selectedItem.name == 'English':
                    _imgInputMetric.isVisible = False
                    _imgInputEnglish.isVisible = True
                    
                    _diaPitch.isVisible = True
                    _module.isVisible = False
    
                    _diaPitch.value = 25.4 / _module.value
                    
                    _units = 'in'
                elif _standard.selectedItem.name == 'Metric':
                    _imgInputMetric.isVisible = True
                    _imgInputEnglish.isVisible = False
                    
                    _diaPitch.isVisible = False
                    _module.isVisible = True
                
                    _module.value = 25.4 / _diaPitch.value
                    
                    _units = 'mm'

                # Set each one to it's current value because otherwised if the user 
                # has edited it, the value won't update in the dialog because 
                # apparently it remembers the units when the value was edited.
                # Setting the value using the API resets this.
                _backlash.value = _backlash.value
                _backlash.unitType = _units
                _rootFilletRad.value = _rootFilletRad.value
                _rootFilletRad.unitType = _units
                _thickness.value = _thickness.value
                _thickness.unitType = _units
                _holeDiam.value = _holeDiam.value
                _holeDiam.unitType = _units
                
            # Update the pitch diameter value.
            diaPitch = None
            if _standard.selectedItem.name == 'English':
                result = getCommandInputValue(_diaPitch, '')
                if result[0]:
                    diaPitch = result[1]
            elif _standard.selectedItem.name == 'Metric':
                result = getCommandInputValue(_module, '')
                if result[0]:
                    diaPitch = 25.4 / result[1]
            if not diaPitch == None:
                if _numTeeth.value.isdigit(): 
                    numTeeth = int(_numTeeth.value)
                    pitchDia = numTeeth/diaPitch

                    # The pitch dia has been calculated in inches, but this expects cm as the input units.
                    des = adsk.fusion.Design.cast(_app.activeProduct)
                    pitchDiaText = des.unitsManager.formatInternalValue(pitchDia * 2.54, _units, True)
                    _pitchDiam.text = pitchDiaText
                else:
                    _pitchDiam.text = ''                    
            else:
                _pitchDiam.text = ''

            if changedInput.id == 'pressureAngle':
                if _pressureAngle.selectedItem.name == 'Custom':
                    _pressureAngleCustom.isVisible = True
                else:
                    _pressureAngleCustom.isVisible = False                    
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        
        
# Event handler for the validateInputs event.
class GearCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
            
            _errMessage.text = ''

            # Verify that at lesat 4 teath are specified.
            if not _numTeeth.value.isdigit():
                _errMessage.text = 'The number of teeth must be a whole number.'
                eventArgs.areInputsValid = False
                return
            else:    
                numTeeth = int(_numTeeth.value)
            
            if numTeeth < 4:
                _errMessage.text = 'The number of teeth must be 4 or more.'
                eventArgs.areInputsValid = False
                return
                
            # Calculate some of the gear sizes to use in validation.
            if _standard.selectedItem.name == 'English':
                result = getCommandInputValue(_diaPitch, '')
                if result[0] == False:
                    eventArgs.areInputsValid = False
                    return
                else:
                    diaPitch = result[1]
            elif _standard.selectedItem.name == 'Metric':
                result = getCommandInputValue(_module, '')
                if result[0] == False:
                    eventArgs.areInputsValid = False
                    return
                else:
                    diaPitch = 25.4 / result[1]

            diametralPitch = diaPitch / 2.54
            pitchDia = numTeeth / diametralPitch
            
            if (diametralPitch < (20 *(math.pi/180))-0.000001):
                dedendum = 1.157 / diametralPitch
            else:
                circularPitch = math.pi / diametralPitch
                if circularPitch >= 20:
                    dedendum = 1.25 / diametralPitch
                else:
                    dedendum = (1.2 / diametralPitch) + (.002 * 2.54)                

            rootDia = pitchDia - (2 * dedendum)        
                    
            if _pressureAngle.selectedItem.name == 'Custom':
                pressureAngle = _pressureAngleCustom.value
            else:
                if _pressureAngle.selectedItem.name == '14.5 deg':
                    pressureAngle = 14.5 * (math.pi/180)
                elif _pressureAngle.selectedItem.name == '20 deg':
                    pressureAngle = 20.0 * (math.pi/180)
                elif _pressureAngle.selectedItem.name == '25 deg':
                    pressureAngle = 25.0 * (math.pi/180)
            baseCircleDia = pitchDia * math.cos(pressureAngle)
            baseCircleCircumference = 2 * math.pi * (baseCircleDia / 2) 

            des = adsk.fusion.Design.cast(_app.activeProduct)

            result = getCommandInputValue(_holeDiam, _units)
            if result[0] == False:
                eventArgs.areInputsValid = False
                return
            else:
                holeDiam = result[1]
                           
            if holeDiam >= (rootDia - 0.01):
                _errMessage.text = 'The center hole diameter is too large.  It must be less than ' + des.unitsManager.formatInternalValue(rootDia - 0.01, _units, True)
                eventArgs.areInputsValid = False
                return

            toothThickness = baseCircleCircumference / (numTeeth * 2)
            if _rootFilletRad.value > toothThickness * .4:
                _errMessage.text = 'The root fillet radius is too large.  It must be less than ' + des.unitsManager.formatInternalValue(toothThickness * .4, _units, True)
                eventArgs.areInputsValid = False
                return
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))"""

