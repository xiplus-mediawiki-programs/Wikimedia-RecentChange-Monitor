import traceback


def main(M, log):
    try:
        if log['type'] != 'abuselog':
            return

        M.addRC_log_abuselog(log)

    except Exception:
        traceback.print_exc()
        M.error(traceback.format_exc())
