"""Used for plotting test statistics"""


import matplotlib.pyplot as plot

from logger import log
from sqldb import db
import config


def _subplotstat(text, stat1, stat2, subnumber, yticks):
    """Create a subplot of a given statistic
    text -- Y label description, e.g. 'CPU [%]'
    stat1 -- first parameter statistics as tuple
    stat2 -- second parameter statistics as tuple
    subnumber -- position to place subplot in main plot, e.g. 312
    yticks -- (optional) Y axis range"""

    log.debug("Creating subplot: " + text)

    # X axis settings
    xlabel1 = [x * config.period for x in range(0, len(stat1))]
    xlabel2 = [x * config.period for x in range(0, len(stat2))]

    maxxsize = int(max(max(xlabel1), max(xlabel2)))
    xgrid = range(0, maxxsize, maxxsize / 4)

    plot.subplot(subnumber)
    plot.plot(xlabel1, stat1, 'r--', xlabel2, stat2, '')
    plot.ylabel(text)
    plot.xticks(xgrid)
    if yticks is not None:
        plot.yticks(yticks)
    plot.grid(True)


def plotstats(image=None, testnumber=""):
    """Get CPU, Memory and Thread statistics from database and plot them
    image -- (optional) object to write plot
    testnumber -- unique test number in database
    return -- PNG object"""

    log.whoami(__name__)
    log.debug("Connecting to database")

    db.open()
    cpu1, mem1, thx1 = db.getstats(db.gettablename(config.vlan['ver1'],
                                                    testnumber))
    cpu2, mem2, thx2 = db.getstats(db.gettablename(config.vlan['ver2'],
                                                    testnumber))
    db.close()

    log.debug("Plotting statistics")

    _subplotstat('CPU [%]', cpu1, cpu2, 311, range(0, 101, 10))

    plot.legend("12", bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                ncol=2, mode="expand", borderaxespad=0.)

    _subplotstat('Mem [MB]', mem1, mem2, 312, None)
    _subplotstat('Threads [number]', thx1, thx2, 313,
        range(min(min(thx1), min(thx2)) - 1, max(max(thx1), max(thx2)) + 2, 2))

    plot.xlabel('Time [s]')
    if image is not None:
        plot.savefig(image, format='png')

    plot.clf()  # Without this plot might keep old data...
