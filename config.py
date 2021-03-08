import os
from enum import Enum


class Verdict(Enum):
    WAITING = -2
    JUDGING = -1
    ACCEPTED = 0
    COMPILE_ERROR = 2


TRACEBACK_LIMIT = 5
