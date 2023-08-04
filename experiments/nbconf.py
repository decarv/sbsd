import sys
import os

sys.path.append(os.path.abspath("../src"))

sys.path.append(os.path.abspath(".."))

import config

module = globals().get('config', None)
