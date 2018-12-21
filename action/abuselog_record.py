import traceback
import json
from Monitor import *


def main(log):
    M = Monitor()
    try:
        M.addRC_log_abuselog(log)

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc())
