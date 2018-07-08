import sys, adsk.core, traceback, json, datetime
from importlib import reload
from ast import literal_eval
from aide_gui import helper

# Import local dependencies.
sys.path.append(helper.abs_path('./dependencies'))
from jinja2 import Environment, FileSystemLoader, select_autoescape

f360_event_handlers = []

page_templates = Environment(
     loader = FileSystemLoader(helper.abs_path('data/templates')),
     autoescape = select_autoescape(['html', 'xml'])
)
dropdown_structure = helper.load_yaml(helper.abs_path('data/dropdown.yaml'))

def run(context, other_aide_modules):
    try:
        global f360_ui, f360_app, run_other_aide_modules
        f360_app = adsk.core.Application.get()
        f360_ui  = f360_app.userInterface
        run_other_aide_modules = other_aide_modules

        reload(helper)

        # NOTE: This "button" is not actually rendered in the Fusion 360 UI. When the add-in is run, the command associated with the "button" is called immediately to render the palette.
        show_palette_button = f360_ui.commandDefinitions.addButtonDefinition('showPalette', '', '')
        event_handler = ShowPaletteCommandCreatedHandler()
        show_palette_button.commandCreated.add(event_handler)
        f360_event_handlers.append(event_handler)

        show_palette_button.execute()

    except:
        if f360_ui:
            f360_ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class ShowPaletteCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            show_palette_command = args.command
            event_handler = ShowPaletteCommandExecuteHandler()
            show_palette_command.execute.add(event_handler)
            f360_event_handlers.append(event_handler)

        except:
            f360_ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class ShowPaletteCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            command = {
                'action' : 'home',
                'src' : helper.load_yaml(helper.abs_path('data/structure.yaml'))
            }
            helper.render_page(page_templates, dropdown_structure, command)

            palette = f360_ui.palettes.add(
                'aide_gui', # ID
                'AguaClara Infrastructure Design Engine', # Displayed name
                helper.abs_path('data/display.html'), # Displayed page
                True, # Visible
                False, # Show close button
                True # Resizable
            )
            palette.setMinimumSize(300, 400)
            palette.dockingState = adsk.core.PaletteDockingStates.PaletteDockStateRight

            event_handler = HTMLEventHandler()
            palette.incomingFromHTML.add(event_handler)
            f360_event_handlers.append(event_handler)

        except:
            f360_ui.messageBox('Failed: \{}'.format(traceback.format_exc()))

class HTMLEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            html_event = adsk.core.HTMLEventArgs.cast(args)
            command = json.loads(html_event.data)

            if command['action'] == 'user_input':
                helper.write_yaml('data/params.yaml', command['src'])
                run_other_aide_modules()

            elif command['action'] == 'dropdown':
                command = {
                    'action' : 'home',
                    'src' : helper.load_yaml(helper.abs_path('data/structure.yaml'))
                }
                helper.render_page(page_templates, dropdown_structure, command)
                palette = f360_ui.palettes.itemById('aide_gui')
                palette.htmlFileURL = helper.abs_path('data/display.html')

            else:
                # Convert command['src'] from string to dict.
                command['src'] = literal_eval(command['src'])

                helper.render_page(page_templates, dropdown_structure, command)
                palette = f360_ui.palettes.itemById('aide_gui')
                palette.htmlFileURL = helper.abs_path('data/display.html')

        except:
            f360_ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        palette = f360_ui.palettes.itemById('aide_gui')
        palette.deleteMe()

        show_palette_button = f360_ui.commandDefinitions.itemById('showPalette')
        show_palette_button.deleteMe()
        
    except:
        if f360_ui:
            f360_ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
