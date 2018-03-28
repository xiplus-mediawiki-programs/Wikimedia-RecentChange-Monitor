# -*- coding: utf-8 -*-
import pymysql
import configparser
import json
import os
import sys
import re
import urllib
from sseclient import SSEClient as EventSource
import cgi
from Monitor import *

os.environ['TZ'] = 'UTC'

config = configparser.ConfigParser()
configpath = os.path.dirname(os.path.realpath(__file__))+'/config.ini'
config.read(configpath)

db = pymysql.connect(host=config.get('database', 'host'),
					 user=config.get('database', 'user'),
					 passwd=config.get('database', 'passwd'),
					 db=config.get('database', 'db'),
					 charset=config.get('database', 'charset'))
cur = db.cursor()
url = 'https://stream.wikimedia.org/v2/stream/recentchange'

defaultwiki = config.get('monitor', 'defaultwiki')
followwiki = json.loads(config.get('monitor', 'followwiki'))
recordwiki = json.loads(config.get('monitor', 'recordwiki'))
blockreasonblacklist = config.get('monitor', 'blockreasonblacklist')

M = Monitor()

for event in EventSource(url):
	if event.event == 'message':
		try:
			change = json.loads(event.data)
		except ValueError:
			continue

		try:
			M.change_wiki_and_domain(change['wiki'], change["meta"]["domain"])

			wiki = change["wiki"]
			ctype = change["type"]
			user = change["user"]
			title = change["title"]
			comment = change["comment"]

			issend = False
			isrecord = (wiki in recordwiki)
			message_append = ""

			if wiki != defaultwiki:
				message_append += "("+wiki+")"

			rows = M.check_user_blacklist(user)
			if len(rows) != 0:
				issend = True
				isrecord = True
				message_append += "\n(blacklist: "+cgi.escape(rows[0][0], quote=False)
				if rows[0][2] != "" and rows[0][2] != user:
					message_append += "("+rows[0][2]+")"
				message_append += ', '+M.formattimediff(rows[0][1])+")"

			rows = M.check_page_blacklist(title, wiki)
			if len(rows) != 0 and len(M.check_user_whitelist(user)) != 0:
				issend = True
				isrecord = True
				message_append += "\n(watch: "+cgi.escape(rows[0][0], quote=False)+', '+M.formattimediff(rows[0][1])+")"

			if change["bot"]:
				issend = False

			if wiki not in followwiki and not isrecord:
				continue

			if ctype == "edit":
				isrecord and M.addRC_edit(change)

				print(user+" edit "+title)
				message = M.link_user(user)+' edit '+M.link_page(title)+' ('+M.link_diff(change["revision"]["new"])+')'
				issend and M.sendmessage(message+message_append)
			elif ctype == "new":
				isrecord and M.addRC_new(change)

				print(user+" create "+title)
				message = M.link_user(user)+' create '+M.link_page(title)
				issend and M.sendmessage(message+message_append)
			elif ctype == "142":
				isrecord and M.addRC_142(change)
			
			elif ctype == "categorize":
				isrecord and M.addRC_categorize(change)

				print(user+" categorize "+title)
			elif ctype == "log":
				log_type = change["log_type"]
				log_action = change["log_action"]
				if log_type == "move":
					isrecord and M.addRC_log_move(change)

				elif log_type == "block":
					print(user+" "+log_action+" "+title+" comment:"+change["log_action_comment"])

					if len(M.check_user_blacklist(title[5:])) != 0:
						issend = True

					message = M.link_user(user)+' '+log_action+' '+M.link_user(title[5:])+' ('+cgi.escape(change["log_action_comment"], quote=False)+')'
					issend and M.sendmessage(message+message_append)

					if log_action == "unblock":
						isrecord and M.addRC_log_block_unblock(change)
					else :
						isrecord and M.addRC_log_block(change)
						if re.search(blockreasonblacklist, change["comment"], re.IGNORECASE) != None:
							reason = "blocked on "+wiki+": "+change["comment"]
							user_type = M.user_type(title[5:])
							if type(user_type) != User and user_type.start != user_type.end:
								M.addblack_user(title[5:], change["timestamp"], reason, msgprefix="auto ", wiki=wiki)
							else:
								M.addblack_user(title[5:], change["timestamp"], reason, msgprefix="auto ", wiki="global")

				elif log_type == "protect":
					if log_action == "unprotect":
						isrecord and M.addRC_log_protect_unprotect(change)
						
						print(user+" unprotect "+title+" comment:"+comment)
					elif log_action == "move_prot":
						isrecord and M.addRC_log_protect_move_prot(change)

						print(user+" move_prot "+title+" comment:"+comment)
					else :
						isrecord and M.addRC_log_protect(change)

						print(user+" protect "+title+" comment:"+comment)
						message = M.link_user(user)+' '+log_action+' '+M.link_page(title)+' ('+cgi.escape(comment, quote=False)+') ('+cgi.escape(change["log_params"]["description"], quote=False)+')'
						issend and M.sendmessage(message+message_append)

				elif log_type == "newusers":
					isrecord and M.addRC_log_newusers(change)

					print(user+" newusers "+title)
				elif log_type == "thanks":
					isrecord and M.addRC_log_thanks(change)

				elif log_type == "patrol":
					isrecord and M.addRC_log_patrol(change)

				elif log_type == "upload":
					isrecord and M.addRC_log_upload(change)

				elif log_type == "rights":
					isrecord and M.addRC_log_rights(change)

				elif log_type == "renameuser":
					isrecord and M.addRC_log_renameuser(change)

				elif log_type == "merge":
					isrecord and M.addRC_log_merge(change)

				elif log_type == "delete":
					if log_action == "delete":
						isrecord and M.addRC_log_delete(change)

					elif log_action == "delete_redir":
						isrecord and M.addRC_log_delete(change)

					elif log_action == "restore":
						isrecord and M.addRC_log_delete_restore(change)

					elif log_action == "revision":
						isrecord and M.addRC_log_delete_revision(change)

				elif log_type == "abusefilter":
					if log_action == "hit":
						isrecord and M.addRC_log_abusefilter_hit(change)

						print(user+" hit af "+str(change["log_params"]["filter"])+" in "+title)
					elif log_action == "modify":
						isrecord and M.addRC_log_abusefilter_modify(change)

						message = M.link_user(user)+' modify '+M.link_abusefilter(change["log_params"]["newId"])+' ('+M.link_all('Special:Abusefilter/history/'+str(change["log_params"]["newId"])+'/diff/prev/'+str(change["log_params"]["historyId"]), 'diff')+')'

						if wiki in followwiki:
							issend = True

						issend and M.sendmessage(message+message_append)
						
			if not isrecord:
				print(json.dumps(change, indent=4, sort_keys=True, ensure_ascii=False))

			if (wiki in followwiki and ctype in ["edit", "new"]) and change["namespace"] == 3 and re.match(r"^User talk:", title) and re.match(r"^(層級|层级)[234]", comment):
				reason = "warn by "+user+": "+comment
				M.addblack_user(title[10:], change["timestamp"], reason, msgprefix="auto ")

		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			M.error(str(e)+" "+json.dumps(change))
			M.error(str(exc_type)+" "+str(fname)+" "+str(exc_tb.tb_lineno))
			print(e)
			print(exc_type, fname, exc_tb.tb_lineno)
