import os
import sys

dir_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(dir_path))
sys.path.insert(1, os.path.abspath(os.path.join(dir_path, "..")))
