import pathlib
from os.path import dirname, realpath, sep, pardir
import sys

sys.path.append(str(pathlib.Path(dirname(realpath(__file__))+"../../../..").resolve()))