import traceback

from Monitor import Monitor


def main(log):
    M = Monitor()
    try:
        M.addRC_log_abuselog(log)

    except Exception:
        traceback.print_exc()
        M.error(traceback.format_exc())
