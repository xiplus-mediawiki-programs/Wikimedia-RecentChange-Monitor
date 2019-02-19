# -*- coding: utf-8 -*-
import argparse
import os
import sys

import requests

sys.path.insert(0, os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../"))
from Monitor import Monitor  # noqa: E402, pylint: disable=C0413


parser = argparse.ArgumentParser()
parser.add_argument('action', default='set')
parser.add_argument('--url')
parser.add_argument('--max_connections', default=40)
args = parser.parse_args()
print(args)

M = Monitor()

if args.action == 'set':
    url = "https://api.telegram.org/bot{0}/setWebhook?url={1}&max_connections={2}".format(
        M.token, args.url, args.max_connections)
elif args.action == 'delete':
    url = "https://api.telegram.org/bot{0}/deleteWebhook".format(M.token)
elif args.action == 'get':
    url = "https://api.telegram.org/bot{0}/getWebhookInfo".format(M.token)
else:
    exit('unknown action.')

response = requests.get(url)
print(response.text)
