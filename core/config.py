"""
Configuration file is a regular Python module.
"""

vlan = {'ver1': "vlc-1.1.12",
        'ver2': "vlc-2.0.4",
    'url': "http://download.videolan.org/pub/videolan/vlc/{}/{}.tar.xz"
}

videourl = "http://download.microsoft.com/download/6/8/f/\
68f212d7-f58d-4542-890d-65d7e790f2e0/The_Magic_of_Flight_720.exe"

# Sampling period in seconds
period = 2

# Flags for optional tasks
valgrind = False
gcov = True

downloaddir = "downloads/"

# SQLite3
dbname = 'logs/testtask.db'

# Available log levels are: (from most to least messages)
# DEBUG, INFO, WARNING, ERROR, CRITICAL
loglevel = {'console': 'DEBUG',
            'file': 'INFO'
}

# E-mail settings for notifications
email = {'from': 'skype.test.task@gmail.com',
         'password': '13skype.test.task',
         'to': 'you@example.com',
         'send': False
}
