# -*- coding: utf-8 -*-
import importlib
import json
import logging
import os
import sys
import time
import traceback

import pymysql
from celery import Celery

from Monitor import Monitor

logging.basicConfig(format='%(asctime)s [%(filename)20s:%(lineno)4s] %(levelname)7s %(message)s')

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/action")

celery = Celery('wmrcm')
celery.config_from_object('rc_config')

M = Monitor()
M.load_abusefilter_mode()

os.environ['TZ'] = 'UTC'

try:
    from rc_config import module_list
    logging.info("module_list: %s", module_list)
except ImportError as e:
    if str(e) == "No module named 'rc_config'":
        traceback.print_exc()
    elif str(e) == "cannot import name 'module_list'":
        traceback.print_exc()
    else:
        logging.error(traceback.format_exc())
        raise e

if not isinstance(module_list, list):
    logging.error("module_list is not a list")
    exit()

modules = []
for module_name in module_list:
    if not isinstance(module_name, str):
        logging.error("module_name '{}' is not a str".format(str(module_name)))
        exit()
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, "main") or not callable(module.main):
            logging.error("modue '{}' does not contain main function".format(module_name))
            exit()
        modules.append(module.main)
    except ImportError as e:
        logging.error(traceback.format_exc())
        raise e


from rc_config import LAG_LIMIT


@celery.task(name='wmrcm.process', queue='wmrcm')
def process(rawdata):
    logging.info(rawdata)
    try:
        change = json.loads(rawdata)
    except json.decoder.JSONDecodeError as e:
        msg = 'UnicodeDecodeError: {}. {}'.format(e, rawdata)
        logging.error(msg)
        return

    if int(change['timestamp']) < time.time() - LAG_LIMIT:
        return

    for module in modules:
        try:
            module(M, change)
        except Exception as e:
            if not isinstance(e, (pymysql.err.InterfaceError, pymysql.err.OperationalError)):
                logging.error(traceback.format_exc())
