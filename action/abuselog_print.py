import traceback


def main(M, log):
    try:
        if log['type'] != 'abuselog':
            return

        log_temp = log.copy()
        if 'details' in log_temp:
            KEY_TO_REMOVE = [
                'added_lines',
                'added_links',
                'edit_diff',
                'edit_diff_pst',
                'new_html',
                'new_pst',
                'new_wikitext',
                'old_wikitext',
                'page_first_contributor',
                'removed_lines',
                'removed_links',
                'tor_exit_node',
                'user_groups',
                'user_rights',
            ]
            for key in KEY_TO_REMOVE:
                if key in log_temp['details']:
                    del log_temp['details'][key]
            del log_temp['details']
        print(log_temp)

    except Exception:
        traceback.print_exc()
        M.error(traceback.format_exc())
