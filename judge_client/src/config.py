"""
Load and check configurations.
"""

import os
import logging
import configparser

import define


@define.singleton
class Config(configparser.ConfigParser):
    """
    Singleton class.
    Used to load, store and check configurations.
    """
    def __init__(self, filepath=os.path.join(os.path.dirname(__file__), '../conf/judge.conf')):
        self.logger = logging.getLogger('JudgeCore')
        self.logger.info("....Reading config from {}".format(filepath))

        super().__init__()
        try:
            if not super().read(filepath):
                raise define.JudgeCoreError("ERROR - Config file not exist.")
        except configparser.Error:
            raise define.JudgeCoreError("ERROR - Config file is broken.")


config = Config()

