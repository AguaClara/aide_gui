import os, sys, inspect


def abs_path(file_path):
    """
    Takes a relative file path to the calling file and returns the correct
    absolute path.
    Needed because the Fusion 360 environment doesn't resolve relative paths
    well.
    """
    return os.path.join(os.path.dirname(inspect.getfile(sys._getframe(1))), file_path)
