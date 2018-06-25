import sys, adsk.core, traceback, json, datetime
from importlib import reload
from ast import literal_eval

# NOTE: This can be changed to "from aide_gui.helper import display" once development on helper has been finalized. Also see "reload(helper)" and "helper.display" statements below.
from aide_gui import helper

# Allows Python to search for packages in the directory where this file is located.
sys.path.append(helper.abs_path('./dependencies'))

from jinja2 import Environment, FileSystemLoader, select_autoescape

# Dropdown only needs to be fetched once.
# TODO: Use back buttons for more intuitive navigation. Also see helper.display.
dropdown = helper.load_yaml(helper.abs_path('data/dropdown.yaml'))

# Global set of event handlers to keep them referenced while the palette is being run.
handlers = []

# Global set of variables to render the palette in Fusion 360.
app = adsk.core.Application.cast(None)
ui = adsk.core.UserInterface.cast(None)

# Specify the HTML templates that are rendered through Jinja2.
env = Environment(
     loader = FileSystemLoader(helper.abs_path('data/templates')),
     autoescape = select_autoescape(['html', 'xml'])
)

# Event handler for creating the command to show the palette.
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

# Event handler for executing the command to show the palette.
class ShowPaletteCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # Render the Home page.
            palette = ui.palettes.itemById('aide_gui')
            command={
                'action' : 'home',
                'src' : helper.load_yaml(helper.abs_path('data/structure.yaml'))
            }

            # NOTE: This can be changed to "display(...)" once development on helper has been finalized.
            helper.display(env, dropdown, command)

            # Initialize the palette.
            palette = ui.palettes.add(
                'aide_gui', 'AguaClara Infrastructure Design Engine', helper.abs_path('data/display.html'), # ID, Displayed name, Displayed HTML
                True, False, True # Visible, Close button, Resizable
            )
            palette.setMinimumSize(300, 400)

            # Dock the palette to the right side of Fusion window.
            palette.dockingState = adsk.core.PaletteDockingStates.PaletteDockStateRight

            # Add handler to HTMLEvent of the palette.
            onHTMLEvent = MyHTMLEventHandler()
            palette.incomingFromHTML.add(onHTMLEvent)
            handlers.append(onHTMLEvent)
        except:
            ui.messageBox('Failed: \{}'.format(traceback.format_exc()))

# Event handler for executing clicks from the HTML.
class MyHTMLEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # Receive data from the HTML and convert to dict.
            htmlArgs = adsk.core.HTMLEventArgs.cast(args)
            command = json.loads(htmlArgs.data)

            # Send user parameters (if given) to YAML.
            if command['action'] == 'collect':
                # TODO: Rename collect across everything to user_input.
                # TODO: Don't write to locations where code is located.
                helper.write_yaml('params.yaml', command['src'])

            # NOTE: This is a temporary fix until a back button can be figured out.
            elif command['action'] == 'dropdown':
                command={
                    'action' : 'home',
                    'src' : helper.load_yaml(helper.abs_path('data/structure.yaml'))
                }
                helper.display(env, dropdown, command)
                palette = ui.palettes.itemById('aide_gui')
                palette.htmlFileURL = helper.abs_path('data/display.html')

            else:
                # Convert command['src'] from string to dict.
                command['src'] = literal_eval(command['src'])

                # Render a new page.
                # NOTE: This can be changed to "display(...)" once development on helper has been finalized.
                helper.display(env, dropdown, command)
                palette = ui.palettes.itemById('aide_gui')
                palette.htmlFileURL = helper.abs_path('data/display.html')
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    try:
        # Load global variables for use in events.
        global ui, app, env
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Reload functions from helper if changes have been made.
        # NOTE: This can be deleted once development on helper has been finalized.
        reload(helper)

        # Add a command that displays the panel.
        showPaletteCmdDef = ui.commandDefinitions.addButtonDefinition('showPalette', '', '')

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
        palette = ui.palettes.itemById('aide_gui')
        if palette:
            palette.deleteMe()

        # Delete controls and associated command definitions created by this add-in.
        cmdDef = ui.commandDefinitions.itemById('showPalette')
        if cmdDef:
            cmdDef.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
