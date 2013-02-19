1. Requirements:
    * Debian based Linux (tested on Ubuntu 12.04.1 x64)
    * Python 2.6 (tested on Python 2.7)
    * Internet connection
    * At least 500 MB of free disk space
    * 3D acceleration


﻿2. Installation:
    Run install.sh script to install all required dependencies.


3. Execution:
    * To run Test Task script you can make it executable:
        "sudo chmod a+x testtask.py"
    and simply call it by:
        "./testtask.py"
    Or start Python with "testtask.py" as argument
        "python testtask.py"

    * To view results open web browser and go to http://127.0.0.1:5000
    (to quit flask HTTP server just go to http://127.0.0.1:5000/shutdown)


4. Contributing:
    Please verify your code with below tools before submitting
        1) pep8 --show-source --show-pep8 --statistics --count --benchmark testtask.py core/
    Expected result is 4 lines of statistics
        2) pylint --rcfile=core/pylint.conf testtask.py /core
    Expected result is overall score 10/10


5. To do list:
    0) Add argparse with clean option 
    1) Save output from VLC build
    2) Unittest API and Core
    3) Parse output from subprocesses for errors; if any don't stamp as done
    4) Performance improvements (e.g. instead of INSERTing every read into DB, save statistics in memory and INSERT it at once)
    5) Add meldiff like functionality to compare output from valgrind/gcov
    6) gconv: filter results (e.g. remove files without entries); capture when video is playing;
    7) More statistics: build time, tar size, extracted size, number of files, load time, output from VLC (number of errors, delay, etc.), average CPU/memory usage
    8) Add VLC API support and a way to choose between it and CMD
    9) Minor improvements: threads plot should be discret (one can't have float number of threads); list of test cases sorter in reverse order; fix short period issue with start/end block timestamps (period - block_time)


6. Comments
    1) why psutil: it's multiplatform and offers high level API; also Linux 'ps' has no current CPU usage while 'top' is slow
    2) development took place on a fresh Linux installation; using extensively modified system can caused issues when compiling VLC (e.g. build system uses 'grep' with options from '.bashrc', so having default 'grep' returning line numbers, causes 'make' to fail)
    3) why flask and sqlite3: they're small, easy and fast (based on research on StackOverflow and LinkedIn groups)
    4) possible update needed in Python's docs ('cwd' description on http://docs.oython.org/2/library/subprocess.html)
    5) why valgrind: it's free and commonly used tool on Linux
    6) why gcov: vlc supports gcov by provifing proper flag to './configure' 
    7) why gcov/valgrind output is store as plain text in sqlite3: default maximum entry size is 1 bilion bytes (roughly 1GB of data), which is far more than their log size
    8) urllib.urlretrieve() is depracated, but still supported (even on Python 3.4)
    9) why decompressing vlc sources with 'subprocess' and 'tar': unfortunately it wasn't until Python 3.3 when 'xz' support was added to built-in zipfile module
    10) why configuration file is Python module: it's not secure, but easy to use, implement and extend; if security was an issue, then e.g. ConfigParser would have been a better choice
    11) SQLite3 and variable table names: "".format() is used, because default formatting (i.e. including '?') doesn't support variable table name
