#-*- coding: UTF-8 -*-

"""
Define decorators and exceptions.
"""

import logging
from enum import Enum


def singleton(class_):
    """
    Singleton decorator.
    Used to decorate a class.
    """
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


class JudgeCoreError(Exception):
    """
    Judge Core Error.
    """
    def __init__(self, errorValue):
        self.value = errorValue
        self.logger = logging.getLogger('JudgeCore')
        self.printToLog()

    def __str__(self):
        return self.value

    def printToLog(self):
        """
         Print Error message to log file.
        """
        self.logger.error("JudgeCoreError, content = {}".format(
             self.value
        ))


class JudgeStatus(Enum):
    Waiting = 0
    Judging = 1
    Compiling = 2
    Running = 3
    Accepted = 4
    CompileError = 5
    WrongAnswer = 6
    RuntimeError = 7
    TimeLimitExceeded = 8
    MemoryLimitExceeded = 9
    OutputLimitExceeded = 10
    PresentationError = 11
    SystemError = 12


class CodeLanguage(Enum):
    C = 0
    CPP = 1
    JAVA = 2
    PY2 = 3
    PY3 = 4
