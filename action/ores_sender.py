import json
import socket
import traceback

from ores_config import config  # pylint: disable=E0611,W0614


def main(M, change):
    try:
        if change['type'] == 'abuselog':
            return

        wiki = change['wiki']

        if wiki != 'zhwiki':
            return

        if change['namespace'] != 0:
            return

        if change['bot']:
            return

        if change['type'] != 'edit':
            return

        M.change_wiki_and_domain(change['wiki'], change['meta']['domain'])

        M.addRC_wiki(change)

        if 'revision' not in change:
            print(change)
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((config['host'], config['port']))
        data = {
            'revid': change['revision']['new'],
            'summary': change['comment'],
            'user': change['user'],
            'page': change['title'],
            'length_diff': change['length']['new'] - change['length']['old'],
        }
        data = json.dumps(data)
        data = data.encode()
        sock.send(data)
        sock.close()

    except Exception:
        traceback.print_exc()
        M.error(traceback.format_exc())
