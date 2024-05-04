__version__ = "0.0.1"
from .xml import *
from .lmcode import *

# `shell` requires IPython to be installed
try: from .shell import *
except ModuleNotFoundError: pass

