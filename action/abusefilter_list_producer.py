# -*- coding: utf-8 -*-
import argparse
import json
import logging
import os
import sys
import urllib.request

sys.path.insert(0, os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../"))
from Monitor import Monitor  # noqa: E402, pylint: disable=C0413


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(filename)20s:%(lineno)4s] %(levelname)7s %(message)s')


parser = argparse.ArgumentParser()
parser.add_argument('wiki')
parser.add_argument('--user')
parser.add_argument('--hidden', action='store_true')
parser.set_defaults(hidden=False)
args = parser.parse_args()

M = Monitor()

M.db_execute("""SELECT `server_name` FROM `RC_wiki` WHERE `wiki` = %s""", (args.wiki))
domain = M.db_fetchone()
if domain is None:
    logging.error('Cannot get domain')
    exit()
else:
    domain = domain[0]
    logging.info('domain is {}'.format(domain))

url = ('https://{}/w/api.php'
       + '?action=query&list=abusefilters&abfprop=id%7Cdescription'
       + '&abflimit=max&format=json').format(domain)

logging.info('fetching from {}'.format(url))
res = urllib.request.urlopen(url).read().decode('utf8')
res = json.loads(res)

for row in res['query']['abusefilters']:
    M.cur.execute(
        """INSERT INTO `abusefilter`
        (`af_id`, `af_name`, `wiki`) VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE `af_name` = %s""",
        (row['id'], row['description'], args.wiki, row['description'])
    )
M.db.commit()
