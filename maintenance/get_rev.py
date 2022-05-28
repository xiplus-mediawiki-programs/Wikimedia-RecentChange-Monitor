# -*- coding: utf-8 -*-
# import json
import os
import sys
import time
import argparse

os.environ['PYWIKIBOT2_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot
sys.path.insert(0, os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + '/../'))
from Monitor import Monitor  # noqa: E402, pylint: disable=C0413


parser = argparse.ArgumentParser()
parser.add_argument('revid', type=int)
args = parser.parse_args()

M = Monitor()
M.login()
result = M.get_diff(args.revid, torelative='prev')
print(result)

with open('temp/{}.txt'.format(args.revid), 'w', encoding='utf8') as f:
    f.write('\n'.join(result['added_lines']))
