import traceback


def main(M, log):
    try:
        M.addRC_log_abuselog(log)

    except Exception:
        traceback.print_exc()
        M.error(traceback.format_exc())
