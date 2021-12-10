# My stuff
from asset import *
from .datetime import *
from embed import *
from missing import *
from upload import *
from prefix import *


def readable_bool(value: bool) -> str:
    return str(value).replace("True", "yes").replace("False", "no")
