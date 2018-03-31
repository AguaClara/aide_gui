# Author-AIDE GUI
import adsk.core
import adsk.fusion
import adsk.cam
import traceback

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)

# Error Message
_errMessage = adsk.core.TextBoxCommandInput.cast(None)

# Event handlers
_handlers = []

def run(context):
    try:
        global _ui, _app

        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = _ui.commandDefinitions

        # Create a command definition
        cmdDef = cmdDefs.addButtonDefinition('adskaide_guiPythonAddIn',
            'AIDE GUI', 'Loads Radio Button Choices', './resources/AIDE')

        # Get the Create Panel in the model workspace in Fusion
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')

        # Add the button to the bottom of the Create Panel in Fusion
        AIDE_Button = createPanel.controls.addCommand(cmdDef)

        # Connect to the command created event (functions to be written)
        onCommandChoice = CommandChoiceHandler()
        cmdDef.commandCreated.add(onCommandChoice)
        _handlers.append(onCommandChoice)

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        # Cleans up the UI once the add-in is stopped
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        AIDE_Button = createPanel.controls.itemById('adskaide_guiPythonAddIn')

        cmdDef = _ui.commandDefinitions.itemById('adskaide_guiPythonAddIn')
        cmdDef1 = _ui.commandDefinitions.itemById('choice1')
        cmdDef2 = _ui.commandDefinitions.itemById('choice2')

        if AIDE_Button:
            AIDE_Button.deleteMe()
        if cmdDef:
            cmdDef.deleteMe()
        if cmdDef1:
            cmdDef1.deleteMe()
        if cmdDef2:
            cmdDef2.deleteMe()

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

# Creates a window to request yaml local path or url from user
class CommandChoiceHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs

            # Ask for user to specify Choice
            radioButtonGroup = inputs.addRadioButtonGroupCommandInput('radioButtonGroup', 'Choices')
            radioButtonItems = radioButtonGroup.listItems
            radioButtonItems.add("Choice 1", True)
            radioButtonItems.add("Choice 2", False)

            # just put the radio button on global
            globals()['radioButton']=radioButtonGroup

            # Connect to the command related events.
            onChoiceExec = ChoiceExecuteHandler()
            cmd.execute.add(onChoiceExec)
            _handlers.append(onChoiceExec)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class ChoiceExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()


    def notify(self, args):
        try:
            # just retrive the radio button value from global
            choice=globals()['radioButton'].selectedItem.name

            if  choice == 'Choice 1':

                cmdDefs = _ui.commandDefinitions
                # Create a button command definition
                loadButton = cmdDefs.addButtonDefinition('choice1','','')

                # Connect to the command created event to create the window
                onCommandOne = ChoiceOneCreate()
                loadButton.commandCreated.add(onCommandOne)
                _handlers.append(onCommandOne)

                # Execute the command.
                loadButton.execute()


            elif choice == 'Choice 2':
                    cmdDefs = _ui.commandDefinitions
                    # Create a button command definition
                    loadButton = cmdDefs.addButtonDefinition('choice2','','')

                    # Connect to the command created event to create the window
                    onCommandTwo = ChoiceTwoCreate()
                    loadButton.commandCreated.add(onCommandTwo)
                    _handlers.append(onCommandTwo)

                    # Execute the command.
                    loadButton.execute()

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Creates a window thats associated with choice one
class ChoiceOneCreate(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            # Create the globals based on attributes
            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs
            # Connect to the command destroyed event.
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # display form thats linked to choice one
            strInput = inputs.addStringValueInput('string', 'Text1', 'First choice was selected previously')

            # Connect to the command related events.
            onExecute = ChoiceOneExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class ChoiceOneExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            pass
            # Execute whatever thats linked to choice one display

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Creates a window thats associated with choice two
class ChoiceTwoCreate(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            # Create the globals based on attributes
            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs
            # Connect to the command destroyed event.
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # display form thats linked to choice two
            strInput = inputs.addStringValueInput('string', 'Text2', 'Second choice was selected previously')

            # Connect to the command related events.
            onExecute = ChoiceTwoExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class ChoiceTwoExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            pass
            # Execute whatever thats linked to choice two display

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
