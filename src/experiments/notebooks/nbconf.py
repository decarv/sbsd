import sys
import os

sys.path.append(os.path.abspath("../sse"))

import config

module = globals().get('config', None)
print(module.__dict__)
