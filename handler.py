# -*- coding: utf-8 -*-
import importlib
import os
import sys

from flask import Flask, send_file
from flask_cors import CORS

import web  # pylint: disable=W0611
from Monitor import Monitor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), 'web'))

os.environ['TZ'] = 'UTC'

M = Monitor()

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return website('index')


@app.route('/<path>', methods=['GET', 'POST'])
def website(path):
    if path.endswith('.js'):
        return send_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'web', path))
    try:
        module = importlib.import_module('.' + path, 'web')
        print(module)
    except ImportError as e:
        M.log('[handler][error] {}'.format(e))
        return 'No such module.'
    try:
        return module.web()
    except AttributeError as e:
        M.log('[handler][error] {}'.format(e))
        return "This module doesn't have web."


if __name__ == "__main__":
    app.run()
