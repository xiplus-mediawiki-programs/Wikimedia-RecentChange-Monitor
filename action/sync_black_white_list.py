import logging
import re
import subprocess
import traceback

from sync_black_white_list_config import sync_path


def get_comment_user(comment):
    m = re.search(r'^已加入\[\[:User(?: talk)?:([^/\]]+).*\]\]$', comment)
    if m:
        return 'add', m.group(1)
    m = re.search(r'^已移除\[\[:User(?: talk)?:([^/\]]+).*\]\]$', comment)
    if m:
        return 'remove', m.group(1)
    return None, None


def main(M, change):
    try:
        if change['wiki'] not in ['zhwiki']:
            return

        M.change_wiki_and_domain(change['wiki'], change['meta']['domain'])

        if change['type'] == 'edit':
            title = change['title']
            comment = change['comment']

            if title == 'Wikipedia:維基百科政策簡報/List E':
                action, username = get_comment_user(comment)
                logging.info('%s %s %s %s', 'sync', action, username, title)
                if action is not None:
                    args = ['python3.7', sync_path, 'Wikipedia:維基百科政策簡報/List Z', 'Wikipedia:維基百科政策簡報/List E', action, username, str(change['revision']['new'])]
                    logging.info(args)
                    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif title == 'Wikipedia:維基百科政策簡報/List Z':
                action, username = get_comment_user(comment)
                logging.info('%s %s %s %s', 'sync', action, username, title)
                if action == 'add':
                    args = ['python3.7', sync_path, 'Wikipedia:維基百科政策簡報/List Z', 'Wikipedia:維基百科政策簡報/List E', 'badd', username, str(change['revision']['new'])]
                    logging.info(args)
                    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    except Exception:
        traceback.print_exc()
        M.error(traceback.format_exc())
