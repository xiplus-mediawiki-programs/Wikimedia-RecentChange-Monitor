# -*- coding: utf-8 -*-
import pymysql
import configparser
import json
import os
import requests
import pickle
import datetime
import dateutil.parser
import pytz
import sys
from http.cookiejar import CookieJar
from Monitor import Monitor

os.environ['TZ'] = 'UTC'

config = configparser.ConfigParser()
configpath = os.path.dirname(os.path.realpath(__file__))+'/config.ini'
config.read(configpath)

wp_api = config.get('wikipedia', 'api')
wp_user = config.get('wikipedia', 'user')
wp_pass = config.get('wikipedia', 'pass')
wp_user_agent = config.get('wikipedia', 'user_agent')

afblacklist = json.loads(config.get("monitor","afblacklist"))


abusefilter_list = {}
import csv
with open(os.path.dirname(os.path.realpath(__file__))+'/abusefilter_list.csv') as csvfile:
	reader = csv.reader(csvfile)
	for row in reader:
		abusefilter_list[int(row[0])] = row[1]


jar = CookieJar()

session = requests.Session()

try:
	with open('cookie.txt', 'rb') as f:
		cookies = pickle.load(f)
		session.cookies = cookies
except Exception as e:
	print("parse cookie file fail")

print("checking is logged in")
params = {'action': 'query', 'assert': 'user', 'format': 'json'}
res = session.get(wp_api, params = params, cookies = jar).json()
if "error" in res:
	print("fetching login token")
	params = {
		'action': 'query',
		'meta': 'tokens',
		'type': 'login',
		'format': 'json'
		}
	res = session.get(wp_api, params = params, cookies = jar).json()
	logintoken = res["query"]["tokens"]["logintoken"]

	print("logging in")
	params = {
		'action': 'login',
		'lgname': wp_user,
		'lgpassword': wp_pass,
		'lgtoken': logintoken,
		'format': 'json'
		}
	res = session.post(wp_api, data = params, cookies = jar).json()
	if res["login"]["result"] == "Success":
		print("login success")
	else :
		exit("log in fail")

else :
	print("logged in")

with open('cookie.txt', 'wb') as f:
	pickle.dump(session.cookies, f)


M = Monitor()

M.cur.execute("""SELECT `timestamp` FROM `RC_log_abuselog` ORDER BY `timestamp` DESC LIMIT 1""")
timestamp = M.cur.fetchall()[0][0]
timestamp = datetime.datetime.fromtimestamp(timestamp+1, tz=pytz.utc).isoformat().replace('+00:00', 'Z')
print(timestamp)

params = {
		'action': 'query',
		'list': 'abuselog',
		'aflend': timestamp,
		'aflprop': 'ids|user|title|action|result|timestamp|hidden|revid|filter',
		'afllimit': '500',
		'format': 'json'
		}
res = session.get(wp_api, params = params, cookies = jar).json()

try:
	afblacklistname = []
	for id in afblacklist:
		afblacklistname.append(abusefilter_list[id])

	for log in res["query"]["abuselog"]:
		print(log["filter"], log["timestamp"])

		rows = M.check_user_blacklist(log["user"])
		if len(rows) != 0:
			M.sendmessage(M.link_user(log["user"])+' hit '+M.link_abusefilter(log["filter_id"])+' '+log["filter"]+' in '+M.link_page(log["title"])+' ('+M.link_abuselog(log["id"])+')\n(blacklist: '+rows[0][0]+', '+M.formattimediff(rows[0][1])+')')

		if log["filter"] in afblacklistname:
			reason = "hit AF "+log["filter"]
			rows = M.check_user_blacklist_with_reason(log["user"], reason)
			if len(rows) == 0:
				M.addblack_user(log["user"], str(int(dateutil.parser.parse(log["timestamp"]).timestamp())), reason, msgprefix="auto ")
		M.addRC_log_abuselog(log)

except Exception as e:
	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	M.error(str(e))
	M.error(str(exc_type)+" "+str(fname)+" "+str(exc_tb.tb_lineno))
