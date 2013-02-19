"""General test API"""


import urllib
import subprocess
import zipfile
import os
import psutil
import time

from core.logger import log
from core.sqldb import db
from core import config


def startflask():
    """Start flask process, if none is running"""
    for pid in psutil.get_pid_list():
        if "flask" in " ".join(psutil.Process(pid).cmdline):
            log.debug("Flask is already running")
            return

    log.debug("Flask is not running - starting flask...")
    devnull = open(os.devnull, 'wb')  # stdout & stderr are redirected here
    subprocess.Popen(['python', 'core/flaskserver.py', os.getcwd() + '/core'],
                        stdout=devnull, stderr=devnull, close_fds=True)


def init():
    """Prepare test environment"""
    log.debug("Initializing test environment")

    if not os.path.exists(config.downloaddir):
        log.debug("Creating download folder for downloaded files")
        os.makedirs(config.downloaddir)

    if not os.path.exists(".install_log.txt"):
        log.warning("install.sh script wasn't executed!")

    startflask()


def get_vlc(version):
    """Download VLC sources from Internet and extract them
    version -- version of VLC to work with e.g. 2.0.4
    return -- path to VLC binary"""

    if os.path.exists(config.downloaddir + version):
        log.info("VLC {} already downloaded and extracted".format(version))
        return

    log.info("Downloading VLC version {} ".format(version))
    url = config.vlan['url'].format(version[4:], version)
    log.debug(url)
    archvlc, _ = urllib.urlretrieve(url)

    log.info("Extracting VLC sources {} ".format(archvlc))
    subprocess.check_call(['tar', '-C', config.downloaddir, '-Jxf', archvlc])

    return config.downloaddir + version + "/vlc"


def build_vlc(version):
    """Build the vlc from sources (if needed)"""
    stampfile = config.downloaddir + "." + version
    vlcdir = os.getcwd() + "/" + config.downloaddir + version + "/"

    if os.path.exists(stampfile):
        log.info("No need to build {}".format(version))
        return

    subprocess.check_call(["./configure", "--prefix=/usr", "--enable-coverage",
        "--disable-dbus", "--disable-lua", "--disable-mad",
        "--disable-postproc", "--disable-a52", "--disable-fribidi",
        "--enable-pulse", "--enable-alsa"], cwd=vlcdir)

    subprocess.check_call(["make"], cwd=vlcdir)

    open(stampfile, 'w').close()


def get_videofile():
    """Downlaod zipped video, extract it to the download folder
    return -- path to video file"""

    if os.path.exists(config.downloaddir +
                      os.path.basename(config.videourl).replace('exe', 'wmv')):
        log.info("Media file already downloaded and extracted")
        return

    log.info("Downloading media file")
    log.debug(config.videourl)
    videoexe, _ = urllib.urlretrieve(config.videourl)

    log.info("Extracting video from ZIP (sic!)")
    log.debug(videoexe)
    archfile = zipfile.ZipFile(videoexe)
    for f in archfile.namelist():
        mediafile = open(f, "wb")
        mediafile.write(archfile.read(f))
        mediafile.close()
        path = config.downloaddir + mediafile.name
        os.rename(mediafile.name, path)
    archfile.close()

    return path


def getgcov(version):
    """Executes gcov script and returns its output
    version -- version of VLC to get gcov statistics
    return -- gcov output for version"""

    log.info("Collecting gcov data for {}".format(version))
    devnull = open(os.devnull, 'wb')  # stdout & stderr are redirected here)
    proc = subprocess.Popen(['./core/gcov.sh', config.downloaddir + version],
                            stdout=devnull, stderr=devnull)
    proc.wait()

    fp = open("." + version + ".txt", 'r')
    output = fp.read()
    fp.close()

    return output


def _valgrindlog(version):
    """Return name of valgrind log file
    version -- VLC version name
    return -- file name without path"""
    return "." + version + "_val.txt"


def getvalgrind(version):
    """Returns valgrind memcheck file content
    version -- VLC version name
    return -- string from valgrind log file"""
    fp = open(_valgrindlog(version), 'r')
    output = fp.read()
    fp.close()

    return output


def collectstats(vlc, video="downloads/The_Magic_of_Flight_720.wmv"):
    """Executes VLC process and collects resource usage"""
    db.open()
    db.createstattable(vlc)

    logfile = open(_valgrindlog(vlc), 'w')
    vlc = config.downloaddir + vlc + "/vlc"

    if config.valgrind is True:
        proc = subprocess.Popen(["valgrind", vlc, "-I", "dummy",
            "--play-and-exit", "--fullscreen", video], close_fds=True,
            stdout=logfile, stderr=logfile)
    else:
        proc = subprocess.Popen([vlc, "-I", "dummy", "--play-and-exit",
            "--fullscreen", video], close_fds=True)
    psproc = psutil.Process(proc.pid)

    while (proc.poll() is None):
        db.setstats(psproc.get_cpu_percent(), psproc.get_memory_info()[0],
                    psproc.get_num_threads())
        time.sleep(config.period)

    logfile.close()
    db.close()
