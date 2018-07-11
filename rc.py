# -*- coding: utf-8 -*-
import pymysql
import configparser
import json
import os
import re
import urllib
from sseclient import SSEClient as EventSource
import traceback
import importlib
from Monitor import *

os.environ['TZ'] = 'UTC'

url = 'https://stream.wikimedia.org/v2/stream/recentchange'

M = Monitor()

try:
    from rc_config import module_list
    print("module_list", module_list)
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
        module = importlib.import_module("."+module_name, "action")
        if not hasattr(module, "main") or not callable(module.main):
            M.error("modue '{}' does not contain main function".format(module_name))
            exit("modue '{}' does not contain main function\n".format(module_name))
        modules.append(module.main)
    except ImportError as e:
        M.error(traceback.format_exc())
        raise e

for event in EventSource(url):
    if event.event == 'message':
        try:
            change = json.loads(event.data)
        except ValueError:
            continue

        for module in modules:
            try:
                module(change)
            except Exception as e:
                traceback.print_exc()
                M.error(traceback.format_exc())
