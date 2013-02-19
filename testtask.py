#!/usr/bin/env python
"""Test Task itself"""


import time
import sys
sys.dont_write_bytecode = True    # Prevents from creating cache files

from core.sqldb import db
from core.logger import log
import core.config as config
import core.api as api


if __name__ == "__main__":
    api.init()

    starttime = time.time()
    api.get_vlc(config.vlan['ver1'])
    api.get_vlc(config.vlan['ver2'])
    api.get_videofile()

    api.build_vlc(config.vlan['ver1'])
    api.build_vlc(config.vlan['ver2'])

    api.collectstats(config.vlan['ver1'])
    api.collectstats(config.vlan['ver2'])
    endtime = time.time()

    if config.gcov is True:
        gcov = (api.getgcov(config.vlan['ver1']),
                api.getgcov(config.vlan['ver2']))
    else:
        nogcov = "gcov was disabled in config.py file"
        gcov = (nogcov, nogcov)

    if config.valgrind is True:
        valgrind = (api.getvalgrind(config.vlan['ver1']),
                    api.getvalgrind(config.vlan['ver2']))
    else:
        nogvalgrind = "valgrind was disabled in config.py file"
        valgrind = (nogvalgrind, nogvalgrind)

    db.setresult(starttime, endtime, gcov, valgrind)
    log.results()
