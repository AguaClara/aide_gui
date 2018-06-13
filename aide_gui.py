import os, sys, inspect, json, datetime, traceback, importlib
import adsk.core, adsk.fusion, adsk.cam

# Takes a relative file path (String) to the calling file and returns the correct absolute path (String). Needed because the Fusion 360 environment doesn't resolve relative paths well.
def abs_path(file_path):
    return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), file_path)

sys.path.append(abs_path('.'))

from .jinja2 import Environment, FileSystemLoader, select_autoescape
from .helper import jinjafy, load_yaml

link_cards = 'data/home/cards.yaml'
link_dropdown ='data/home/dropdown.yaml'

# Dropdown only needs to be fetched once
dropdown=load_yaml(link_dropdown)


# Global set of event handlers to keep them referenced for the duration of the command.
handlers = []
app = adsk.core.Application.cast(None)
ui = adsk.core.UserInterface.cast(None)
env = Environment(
     loader=FileSystemLoader(abs_path('.')+'/data/templates'),
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
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the commandExecuted event.
class ShowPaletteCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global app, ui, env
            # Create or display the palette.
            palette = ui.palettes.itemById('myPalette')
            if not palette:

                command={
                    'type' : 'home',
                    'link' : link_cards
                }
                # if there was no palette then open homepage
                jinjafy(env, dropdown, command)

                # let palette open the jinjafied.html
                palette = ui.palettes.add('myPalette', 'My Palette', 'jinjafied.html', True, True, True, 300, 200)
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
            ui.messageBox('Failed: \{}'.format(traceback.format_exc()))

# Event handler for the palette HTML event.
class MyHTMLEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            htmlArgs = adsk.core.HTMLEventArgs.cast(args)
            incoming = json.loads(htmlArgs.data)
            # data is what is being sent from pallete in json form

            palette = ui.palettes.itemById('myPalette')
            if (incoming['link'][-5:] == ".yaml"):
                jinjafy(env, dropdown, incoming)
            # Set the html of the palette.
            palette.htmlFileURL = 'jinjafied.html'

            if incoming['type'] == 'collect':
                ui.messageBox('hello')
                with open(abs_path("params.yaml"), 'w') as params_file:
                    yaml.dump(incoming['link'], params_file)

        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    try:
        global ui, app, env
        app = adsk.core.Application.get()
        ui  = app.userInterface

        importlib.reload(helper)

        # Add a command that displays the panel.
        showPaletteCmdDef = ui.commandDefinitions.itemById('showPalette')
        if not showPaletteCmdDef:
            showPaletteCmdDef = ui.commandDefinitions.addButtonDefinition('showPalette', 'Show Palette', 'Show AIDE palette', '')

            # Connect to Command Created event.
            onCommandCreated = ShowPaletteCommandCreatedHandler()
            showPaletteCmdDef.commandCreated.add(onCommandCreated)
            handlers.append(onCommandCreated)

        # Open the palette as soon as the user runs the add-in.
        showPaletteCmdDef.execute()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        # Delete the palette created by this add-in.
        palette = ui.palettes.itemById('myPalette')
        if palette:
            palette.deleteMe()

        # Delete controls and associated command definitions created by this add-in.
        cmdDef = ui.commandDefinitions.itemById('showPalette')
        if cmdDef:
            cmdDef.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
