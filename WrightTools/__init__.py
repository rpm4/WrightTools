"""WrightTools init."""
# flake8: noqa


# --- import --------------------------------------------------------------------------------------


from .__citation__ import *
from .__version__ import *
from .__wt5_version__ import *
from . import artists
from . import collection
from . import data
from . import diagrams
from . import kit
from . import units
from . import exceptions

from ._open import *
from ._close import *
from .collection._collection import *
from .data._data import *


# --- rcparams ------------------------------------------------------------------------------------

artists.apply_rcparams("fast")
