# -*- coding: utf-8 -*-
import os
import sys
import argparse

os.environ['PYWIKIBOT2_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot
sys.path.insert(0, os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + '/../'))
from Monitor import Monitor  # noqa: E402, pylint: disable=C0413


parser = argparse.ArgumentParser()
parser.add_argument('ip')
args = parser.parse_args()
print(args)


M = Monitor()

user = args.ip
userobj = M.user_type(user)
if userobj.isuser:
    exit('not ip')

site = pywikibot.Site()
site.login()
token = site.tokens['csrf']

score = M.get_proxy_score(user)
print(score)
if score >= 3:
    try:
        data = pywikibot.data.api.Request(site=site, parameters={
            'action': 'block',
            'user': user,
            'expiry': '63113904 seconds',
            'reason': '{{blocked proxy}}',
            'anononly': False,
            'nocreate': True,
            'allowusertalk': True,
            # 'reblock': True,
            'token': token
        }).submit()
        print(data)
    except Exception as e:
        print(e)
