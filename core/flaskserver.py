#!/usr/bin/env python
"""Flask server for displaying TestTask result through HTTP"""


import sys
sys.dont_write_bytecode = True    # Prevents from creating cache files

import sqlite3
import time

from flask import Flask, send_file
from flask import request, render_template, g
from cStringIO import StringIO

import config
import plotter


# Server won't start unless template directory is provided as script argument
app = Flask(__name__, template_folder=sys.argv[1])


def shutdown_server():
    """Shutdowns werkzeug server"""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown')
def shutdown():
    """Enter this page to shutdown flask server"""
    shutdown_server()
    return 'Server shutting down...'


@app.route('/image.png')
def image_png():
    """Returns plot of CPU, memory and thread usage"""
    image = StringIO()
    plotter.plotstats(image, request.args.get('test'))
    image.seek(0)
    return send_file(image,
                     attachment_filename="image.png",
                     as_attachment=True)


@app.route('/<test>')
def result(test):
    """Returns result page (for single test)"""
    title = (time.ctime(float(test)), config.vlan['ver1'], config.vlan['ver2'])

    gcov = g.db.execute('SELECT vlc1gcov, vlc2gcov FROM results\
                            WHERE starttime = {}'.format(test)).fetchall()
    valgrind = g.db.execute('SELECT vlc1valgrind, vlc2valgrind FROM results\
                            WHERE starttime = {}'.format(test)).fetchall()

    return render_template('template_result.html', title=title, test=test,
                        valgrind1=valgrind[0][0].replace('\n', '<BR>'),
                        valgrind2=valgrind[0][1].replace('\n', '<BR>'),
                            gcov1=gcov[0][0].replace('\n', '<BR>'),
                            gcov2=gcov[0][1].replace('\n', '<BR>'))


@app.route('/')
def index():
    """Main page to display all test results"""
    results = g.db.execute('SELECT starttime FROM results').fetchall()
    results = [(x[0], time.ctime(x[0])) for x in results]
    return render_template('template_index.html', results=results)


@app.before_request
def before_request():
    """Conect to database before serving request
    (g is "special" flask object - it's recommended way to connect to DB)"""
    g.db = sqlite3.connect(config.dbname)


@app.after_request
def after_request(response):
    """Close DB connection after request was served"""
    g.db.close()
    return response


if __name__ == "__main__":
    app.run(debug=True)
