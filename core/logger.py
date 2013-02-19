"""
logger module is used to output all messages both to a file and user console

log - use this object to describe status of current message
      (debug(), info(), warning(), error() and critical())
"""

# Standard Python modules
import os
import logging
import inspect
from datetime import datetime

# e-mail modules
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import config as config


# Private information about current session with log statistics
_testinfo = {"filename": None,
             "result":   0,  # Highest log level so far (10 debug:50 critical)
             "WARNING":  0,  # Number of warnings
             "ERROR":    0,  # Number of errors
             "CRITICAL": 0}  # Number of critical errors (reserved for API)


def setfilename(testname="testtask"):
    """Create and store log filename for current session
    testname -- name of test"""

    # Create unique file name at first run
    if _testinfo["filename"] is None:
        path = "logs/"
        try:
            os.makedirs(path)
        except OSError:  # folder already exists
            pass

        date = datetime.today()
        _testinfo["filename"] = path
        _testinfo["filename"] += "{:04d}{:02d}{:02d}_{:02d}{:02d}{:02d}_{}".\
                    format(date.year, date.month, date.day, date.hour,
                           date.minute, date.second, testname + ".log")


def getfilename():
    """Returns log filename (with path) for current session"""
    if _testinfo["filename"] is None:
        setfilename()

    return _testinfo["filename"]


def sendmail():
    """Send log file to e-mail address"""
    msg = MIMEMultipart()

    msg['From'] = "TestTask"
    msg['To'] = config.email['to']
    msg['Subject'] = "{} ({}): {} ".format("TestTask",
                    os.path.basename(_testinfo["filename"])[:15],
                    logging.getLevelName(_testinfo["result"]))

    text = "Details can be found in the attached file"
    msg.attach(MIMEText(text))

    attach = getfilename()
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(attach, 'rb').read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename={}'.
                    format(os.path.basename(attach)))
    msg.attach(part)

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(config.email['from'], config.email['password'])
    mailServer.sendmail(config.email['from'],
                        config.email['to'],
                        msg.as_string())
    mailServer.close()


class ColoredConsoleHandler(logging.StreamHandler):

    """Contains all the information on how logs should be displayed on screen
    """

    def emit(self, record):
        """Overriding emit to enable colored console messages and statistics
        """
        color = {"DEBUG":       "\033[1;34m",  # BLUE
                 "INFO":        "\033[1;32m",  # GREEN
                 "WARNING":     "\033[1;33m",  # YELLOW
                 "ERROR":       "\033[1;31m",  # RED
                 "CRITICAL":    "\033[1;41m"}  # WHITE text on RED background

        record.msg = "%15s %s" % \
                    (color[record.levelname] + str(record.levelname),
                     ": " + str(record.msg) + '\x1b[0m')
        logging.StreamHandler.emit(self, record)

        if record.levelno > _testinfo["result"]:
            _testinfo["result"] = record.levelno
        try:
            _testinfo[record.levelname] += 1
        except KeyError:
            pass

    def __init__(self):
        """Set default console log level and output format"""
        super(ColoredConsoleHandler, self).__init__()
        self.setLevel(getattr(logging, config.loglevel['console']))
        self.setFormatter(logging.Formatter('%(asctime)s.%(msecs).03d ' + \
                                            '%(message)s', datefmt='%H:%M:%S'))


class TestTaskLogging(logging.Logger):

    """Default logging class for TestTask"""

    def __init__(self, name):
        """Sets handlers and log level, initializes variables"""
        super(TestTaskLogging, self).__init__(name)

        # Get the logging level and output format for file handler
        setfilename(name)
        fileloglevel = getattr(logging, config.loglevel['file'])
        formatter = logging.Formatter(
                            '%(asctime)s - %(levelname)8s - %(message)s')

        # Create file handler
        filehandler = logging.FileHandler(getfilename())
        filehandler.setLevel(fileloglevel)
        filehandler.setFormatter(formatter)
        self.addHandler(filehandler)

        # Add console handler to logging object
        self.setLevel(logging.DEBUG)
        self.addHandler(ColoredConsoleHandler())

        self.debug("Successfully created log object")
        self.debug("Logging to {}".format(getfilename()))

    def results(self):
        """Last actions before log object is destroyed: adding final results"""
        result = {logging.WARNING:  "Test passed with {} warning(s)",
                  logging.ERROR:    "Test failed with {} error(s)",
                  logging.CRITICAL: "Test failed with {} critical message(s)!"}
        try:
            finalresult = _testinfo["result"]
            self.log(finalresult, result[finalresult].format(
                       _testinfo[logging.getLevelName(finalresult)]))
        except KeyError:
            self.info("Test passed without any warnings")

        if config.email['send']:
            self.debug("Sending e-mail")
            sendmail()

    def whoami(self, callername="", parent=False):
        """
        Logs the name of the function were it's called or its parents' name
        (use this logging function for debugging purposes only!)
        callername -- module/class/etc. name (usually __name__ is sufficient)
        parent -- if False then log caller name; otherwise log caller's parent
        """
        self.debug(callername + " - " + inspect.stack()[1 + parent][3])


log = TestTaskLogging("testtask")
