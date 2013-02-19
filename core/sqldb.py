"""sqldb module provides API for inserting and selecting data from TestTask's
database"""


import sqlite3
import time

import config
from logger import log


class SqlDB():

    """Contains necessary functions for efficient work with SQLite DB"""

    def __init__(self):
        """Check if db file exists with main results table"""
        self.conn = None
        self.c = None
        self.table = [str(int(time.time()))]
        self.open()
        try:  # Create table with main results
            self.c.execute('''CREATE TABLE results (\
                        starttime INTEGER, stoptime INTEGER,\
                        vlc1table TEXT, vlc1gcov TEXT, vlc1valgrind TEXT,\
                        vlc2table TEXT, vlc2gcov TEXT, vlc2valgrind TEXT)''')
            log.debug("Created table results")
        except sqlite3.OperationalError:  # Table already exists
            log.debug("Table results already exists")
        self.close()

    def open(self):
        """Open a connection to database specified in config file"""
        self.conn = sqlite3.connect(config.dbname)
        self.c = self.conn.cursor()

    def close(self):
        """Close the connection to the database"""
        self.conn.commit()
        self.c.close()

    def gettablename(self, version, timestamp):
        """Returns unique table name
        version -- for which version table name will be created
        timestamp -- unique time stamp of test case
        return -- table name for the given arguments"""
        tablename = "\"" + version + timestamp + "\""
        return tablename

    def createstattable(self, version):
        """Creates table for storing process' runtime statistics"""
        tablename = self.gettablename(version, self.table[0])
        self.table.append(tablename)

        # Create table
        try:
            self.c.execute('''CREATE TABLE {} \
                (cpu REAL, mem INTEGER, thread INTEGER)'''.format(tablename))
        except sqlite3.OperationalError:  # Table already exists
            log.critical("Table {} already exists!".format(tablename))
            raise

    def setstats(self, cpu, mem, thx):
        """Writes stats to last created stat table"""
        self.c.execute("INSERT INTO {} VALUES ({},{},{})".format(
            self.table[len(self.table) - 1], cpu, mem / 1048576, thx))

    def getstats(self, tablename):
        """Get collected statistics from tables
        tablname -- name of the table to SELECT stats FROM
        return -- (CPU, Mem, Thread) tuple"""
        selectstats = 'SELECT * FROM {}'.format(tablename)
        return zip(*self.c.execute(selectstats).fetchall())

    def setresult(self, starttime, endtime, gcov, valgrind):
        """Write final results to database
        starttime -- time when test was starter in Unix format, i.e. seconds
        endtime -- time when test has finished in Unix format, i.e. seconds
        gcov -- tuple of gcov results for both versions
        valgrind -- tuple of valgrind results for both versions"""
        results = (int(starttime), int(endtime),
                    self.table[1], gcov[0], valgrind[0],
                    self.table[2], gcov[1], valgrind[1])

        self.open()
        self.c.execute("INSERT INTO results VALUES (?,?,?,?,?,?,?,?)", results)
        self.close()


db = SqlDB()
