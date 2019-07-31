# -*- coding: utf-8 -*-
import importlib
import json
import logging
import os
import sys
import time
import traceback

import pymysql
from sseclient import SSEClient as EventSource

from Monitor import Monitor

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/action")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(filename)15s:%(lineno)4s] %(levelname)7s %(message)s')

os.environ['TZ'] = 'UTC'

url = 'https://stream.wikimedia.org/v2/stream/recentchange'

M = Monitor()

try:
    from rc_config import module_list
    logging.info("module_list: %s", module_list)
except ImportError as e:
    if str(e) == "No module named 'rc_config'":
        traceback.print_exc()
    elif str(e) == "cannot import name 'module_list'":
        traceback.print_exc()
    else:
        M.error(traceback.format_exc())
        raise e

if not isinstance(module_list, list):
    M.error("module_list is not a list")
    exit("module_list is not a list\n")

modules = []
for module_name in module_list:
    if not isinstance(module_name, str):
        M.error("module_name '{}' is not a str".format(str(module_name)))
        exit("module_name '{}' is not a str\n".format(str(module_name)))
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, "main") or not callable(module.main):
            message = ("modue '{}' does not contain main function"
                       .format(module_name))
            M.error(message)
            exit(message)
        modules.append(module.main)
    except ImportError as e:
        M.error(traceback.format_exc())
        raise e

errorWaitTime = 1
while True:
    try:
        for event in EventSource(url):
            if event.event == 'message':
                try:
                    change = json.loads(event.data)
                except ValueError:
                    continue

                noError = True
                for module in modules:
                    try:
                        module(M, change)
                    except Exception as e:
                        if not isinstance(e, (pymysql.err.InterfaceError, pymysql.err.OperationalError)):
                            traceback.print_exc()
                            M.error(traceback.format_exc(), noRaise=True)
                        logging.warning(
                            '(A) %s. Wait %s seconds to retry', e, errorWaitTime)
                        time.sleep(errorWaitTime)
                        errorWaitTime *= 2
                        noError = False

                if noError and errorWaitTime > 1:
                    errorWaitTime //= 2

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc(), noRaise=True)
        logging.warning('(B) %s. Wait %s seconds to retry', e, errorWaitTime)
        print(errorWaitTime)
        time.sleep(errorWaitTime)
        errorWaitTime *= 2
