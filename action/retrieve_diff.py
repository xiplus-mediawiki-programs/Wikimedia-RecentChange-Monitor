# -*- coding: utf-8 -*-
import argparse
import os
import sys

import diff_match_patch as dmp_module
sys.path.insert(0, os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../'))
from Monitor import Monitor  # noqa: E402, pylint: disable=C0413


parser = argparse.ArgumentParser()
parser.add_argument('revid', type=int)
parser.add_argument('dir', type=str, nargs='?', default='temp')
args = parser.parse_args()

if not os.path.exists(args.dir):
    os.makedirs(args.dir)

M = Monitor()
M.login()

result = M.session.get(M.wp_api, params={
    'action': 'query',
    'format': 'json',
    'prop': 'revisions',
    'revids': args.revid,
    'rvprop': 'comment'
}).json()
summary = list(result['query']['pages'].values())[0]['revisions'][0]['comment']

result = M.get_diff(args.revid, torelative='prev')

removed_lines = '\n'.join(result['removed_lines'])
added_lines = '\n'.join(result['added_lines'])

dmp = dmp_module.diff_match_patch()
diff = dmp.diff_main(removed_lines, added_lines)
dmp.diff_cleanupSemantic(diff)

text = summary + '\n'
for word in diff:
    if word[0] == 1:
        text += word[1]

if text == '':
    exit('Nothing to save\n')

print(text)

with open(os.path.join(args.dir, 'zhwiki-{}.txt'.format(args.revid)), 'w', encoding='utf8') as f:
    f.write(text)
