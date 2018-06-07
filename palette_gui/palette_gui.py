import os, sys, inspect, json, math
import adsk.core, adsk.fusion, adsk.cam, traceback

# returns absolute path
def abs_path(file_path):
    return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), file_path)

# add the path to local library
sys.path.append(abs_path('.'))

from . import yaml
from . import urllib3
from .jinja2 import Template, Environment, FileSystemLoader, select_autoescape
from .helper import jinjafy, render, load_yaml


link_cards = 'https://raw.githubusercontent.com/AguaClara/aide_gui/spring-2018/palette_docs/home/cards.yaml'
link_dropdown ='https://raw.githubusercontent.com/AguaClara/aide_gui/spring-2018/palette_docs/home/dropdown.yaml'
# this is loaded here because we want to fetch dropdown once only
dropdown=load_yaml(link_dropdown)


# global set of event handlers to keep them referenced for the duration of the command
handlers = []
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_environment = Environment(
    loader=FileSystemLoader(abs_path('.')+'/templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


# Event handler for the commandCreated event.
class ShowPaletteCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            command = args.command
            onExecute = ShowPaletteCommandExecuteHandler()
            command.execute.add(onExecute)
            handlers.append(onExecute)
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the commandExecuted event.
class ShowPaletteCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global _ui, _app, _environment
            # Create or display the palette.
            palette = _ui.palettes.itemById('myPalette')
            if not palette:

                command={
                    'type' : 'home',
                    'link' : link_cards
                }
                # if there was no palette then open homepage
                jinjafy(_environment, dropdown, command)

                # let palette open the jinjafied.html
                palette = _ui.palettes.add('myPalette', 'My Palette', 'jinjafied.html', True, True, True, 300, 200)
                palette.setMinimumSize(300, 400)
                # palette.setMaximumSize(300, 400)

                # Dock the palette to the right side of Fusion window.
                palette.dockingState = adsk.core.PaletteDockingStates.PaletteDockStateRight

                # Add handler to HTMLEvent of the palette.
                onHTMLEvent = MyHTMLEventHandler()
                palette.incomingFromHTML.add(onHTMLEvent)
                handlers.append(onHTMLEvent)

            else:
                palette.isVisible = True
        except:
            _ui.messageBox('Command executed failed: {}'.format(traceback.format_exc()))

# Event handler for the palette HTML event.
class MyHTMLEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            htmlArgs = adsk.core.HTMLEventArgs.cast(args)
            incoming = json.loads(htmlArgs.data)
            # data is what is being sent from pallete in json form

            palette = _ui.palettes.itemById('myPalette')
            jinjafy(_environment, dropdown, incoming)
            # Set the html of the palette.
            palette.htmlFileURL = 'jinjafied.html'

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



# Event handler for the commandCreated event.
class SendInfoCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            command = args.command
            onExecute = SendInfoCommandExecuteHandler()
            command.execute.add(onExecute)
            handlers.append(onExecute)
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the commandExecuted event.
class SendInfoCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # Send information to the palette.
            palette = _ui.palettes.itemById('myPalette')
            if palette:
                # here we replaced some terms so JSON in js recognizes the form
                palette.sendInfoToHTML('send', str(data).replace("'", '"').replace("None", 'null'))
        except:
            _ui.messageBox('Command executed failed: {}'.format(traceback.format_exc()))



def run(context):
    try:
        global _ui, _app, _environment
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        # Add a command that displays the panel.
        showPaletteCmdDef = _ui.commandDefinitions.itemById('showPalette')
        if not showPaletteCmdDef:
            showPaletteCmdDef = _ui.commandDefinitions.addButtonDefinition('showPalette', 'Show Palette', 'Show AIDE palette', '')

            # Connect to Command Created event.
            onCommandCreated = ShowPaletteCommandCreatedHandler()
            showPaletteCmdDef.commandCreated.add(onCommandCreated)
            handlers.append(onCommandCreated)


        # Add a command under ADD-INS panel which sends information from Fusion to the palette's HTML.
        sendInfoCmdDef = _ui.commandDefinitions.itemById('sendInfoToHTML')
        if not sendInfoCmdDef:
            sendInfoCmdDef = _ui.commandDefinitions.addButtonDefinition('sendInfoToHTML', 'Send info to Palette', 'Send Info to Palette HTML', '')

            # Connect to Command Created event.
            onCommandCreated = SendInfoCommandCreatedHandler()
            sendInfoCmdDef.commandCreated.add(onCommandCreated)
            handlers.append(onCommandCreated)


        # Get the Create Panel in the model workspace in Fusion
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        # Add the button to the bottom of the Create Panel in Fusion
        showPaletteButton= createPanel.controls.addCommand(showPaletteCmdDef)
        sendInfoButton= createPanel.controls.addCommand(sendInfoCmdDef)

        # open the pallete as soon as user presses run()
        showPaletteCmdDef.execute()

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        # Delete the palette created by this add-in.
        palette = _ui.palettes.itemById('myPalette')
        if palette:
            palette.deleteMe()

        # Delete the created buttons under SolidCreatePanel
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')

        showPaletteButton = createPanel.controls.itemById('showPalette')
        if showPaletteButton:
            showPaletteButton.deleteMe()

        sendInfoButton = createPanel.controls.itemById('sendInfoToHTML')
        if sendInfoButton:
            sendInfoButton.deleteMe()

        # Delete controls and associated command definitions created by this add-ins
        cmdDef = _ui.commandDefinitions.itemById('showPalette')
        if cmdDef:
            cmdDef.deleteMe()

        cmdDef = _ui.commandDefinitions.itemById('sendInfoToHTML')
        if cmdDef:
            cmdDef.deleteMe()

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
