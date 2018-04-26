import os, sys, inspect, json
import adsk.core, adsk.fusion, adsk.cam, traceback
# add the path to local library
sys.path.append("/Users/eldorbekpualtov/Desktop/AguaClara/aide_gui/aide_gui/palette_gui")
from jinja2 import Template, Environment, FileSystemLoader
from . import yaml
from . import urllib3

# returns absolute path
def abs_path(file_path):
    return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), file_path)

def load_yaml(fpath):
    """
    Returns a yaml form structure or None, if error occurred

    Parameters
    ----------
    fpath: str
        The local file path/URL for the yaml to be retrieved from

    Return
    --------
    yam: dict
        A dictionary thats extrapolated from yaml format
    """
    # If yaml is retrieved from user's local path
    try:
        with open(abs_path(fpath)) as fp:
            yam = yaml.load(fp)
            if (type(yam) != list and type(yam) != dict):
                raise Exception('This is not a YAML')
            return  yam
    except:
        # If yaml is retrieved from a given url
        try:
            url = fpath.strip()
            http = urllib3.PoolManager()
            r = http.request('GET', url)
            status = r.status # check URL status
            if (status != 200):
                raise Exception('This is not a URL')
            yam =  yaml.load(r.data.decode('utf-8'))
            return yam
        except:
            if _ui:
                _ui.messageBox('Not a YAML or URL \nPlease provide a correct form.')
            return None

link= 'https://raw.githubusercontent.com/AguaClara/aide_gui/spring-2018/aide_gui/palette_docs/home/base.yaml'

data=load_yaml(link)



# jinjafy given the path to the template
def render(template_path, context):
    path, filename = os.path.split(abs_path(template_path))
    return Environment(
        loader = FileSystemLoader(path or './')
    ).get_template(filename).render(context)



# global set of event handlers to keep them referenced for the duration of the command
handlers = []
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)


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
            # Create and display the palette.
            palette = _ui.palettes.itemById('myPalette')
            if not palette:
                context = {'fields': data}
                # render the dictionary values onto the html file
                result = render('base.html', context)

                # create a local html file, with jinjafied values
                with open(abs_path("jinjafied.html"), 'w') as jinjafied:
                    jinjafied.write(result)

                # let palette open the jinjafied.html

                palette = _ui.palettes.add('myPalette', 'My Palette', 'jinjafied.html', True, True, True, 300, 200)


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
            data = json.loads(htmlArgs.data)
            # data is what is being sent from pallete in json form

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
                # we need to figure out how incorporate jinja2 here
                palette.sendInfoToHTML('send', str(data).replace("'", '"').replace("None", 'null'))
        except:
            _ui.messageBox('Command executed failed: {}'.format(traceback.format_exc()))



def run(context):
    try:
        global _ui, _app
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        # Add a command that displays the panel.
        showPaletteCmdDef = _ui.commandDefinitions.itemById('showPalette')
        if not showPaletteCmdDef:
            showPaletteCmdDef = _ui.commandDefinitions.addButtonDefinition('showPalette', 'Show custom palette', 'Show the custom palette', '')

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

        # Testlines
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
