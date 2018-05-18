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
blockblacklistwiki = json.loads(config.get('monitor', 'blockblacklistwiki'))
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
			blackuser = user
			title = change["title"]
			comment = change["comment"]

			issend = False
			isrecord = (wiki in recordwiki)
			unknowntype = True
			message_append = ""

			if wiki != defaultwiki:
				message_append += "("+wiki+")"

			rows = M.check_user_blacklist(user)
			if len(rows) != 0:
				issend = True
				isrecord = True
				message_append += "\n（黑名單：\u200b"+M.parse_wikicode(rows[0][0])+"\u200b"
				if rows[0][2] != "" and rows[0][2] != user:
					message_append += "，\u200b"+rows[0][2]+"\u200b"
					blackuser = rows[0][2]
				message_append += '，'+M.formattimediff(rows[0][1])+"）"
				blackuser += "|"+rows[0][3]
			else :
				blackuser = None

			rows = M.check_page_blacklist(title, wiki)
			if len(rows) != 0 and len(M.check_user_whitelist(user)) != 0:
				issend = True
				isrecord = True
				message_append += "\n（監視："+M.parse_wikicode(rows[0][0])+', '+M.formattimediff(rows[0][1])+"）"

			if change["bot"]:
				issend = False

			if wiki not in followwiki and not isrecord:
				continue

			if ctype == "edit":
				isrecord and M.addRC_edit(change)

				print(user+" edit "+title)
				message = M.link_user(user)+'編輯'+M.link_page(title)+'（'+M.link_diff(change["revision"]["new"])+'）'
				issend and M.sendmessage(message+message_append, blackuser)
				unknowntype = False
			elif ctype == "new":
				isrecord and M.addRC_new(change)

				print(user+" create "+title)
				message = M.link_user(user)+'建立'+M.link_page(title)
				unknowntype = False
				issend and M.sendmessage(message+message_append, blackuser)
			elif ctype == "142":
				isrecord and M.addRC_142(change)
				unknowntype = False
			
			elif ctype == "categorize":
				isrecord and M.addRC_categorize(change)
				unknowntype = False

				print(user+" categorize "+title)
			elif ctype == "log":
				log_type = change["log_type"]
				log_action = change["log_action"]
				if log_type == "move":
					isrecord and M.addRC_log_move(change)
					unknowntype = False

				elif log_type == "block":
					print(user+" "+log_action+" "+title+" comment:"+change["log_action_comment"])

					blockuser = title[5:]

					if len(M.check_user_blacklist(blockuser)) != 0:
						issend = True

					user_type = M.user_type(blockuser)
					if type(user_type) != User and user_type.start != user_type.end:
						blockwiki = wiki
					else:
						blockwiki = "global"

					blockname = {"unblock":"解封", "block": "封禁", "reblock": "重新封禁"}

					message = M.link_user(user)+blockname[log_action]+M.link_user(blockuser)+'（'+M.parse_wikicode(change["log_action_comment"])+'）'
					issend and M.sendmessage(message+message_append, blockuser+"|"+blockwiki)

					if log_action == "unblock":
						isrecord and M.addRC_log_block_unblock(change)
						unknowntype = False
					elif log_action == "block" or log_action == "reblock":
						isrecord and M.addRC_log_block(change)
						if wiki in blockblacklistwiki and re.search(blockreasonblacklist, change["comment"], re.IGNORECASE) != None:
							(not issend) and M.sendmessage(message+message_append, blockuser+"|"+blockwiki)
							reason = "於"+wiki+"封禁："+change["comment"]
							M.addblack_user(blockuser, change["timestamp"], reason, msgprefix="自動", wiki=blockwiki)
						unknowntype = False

				elif log_type == "protect":
					protectname = {"unprotect":"解除保護", "move_prot": "移動保護", "protect": "保護", "modify": "變更保護"}

					if log_action == "unprotect":
						isrecord and M.addRC_log_protect_unprotect(change)
						
						print(user+" unprotect "+title+" comment:"+comment)
						unknowntype = False
					elif log_action == "move_prot":
						isrecord and M.addRC_log_protect_move_prot(change)

						print(user+" move_prot "+title+" comment:"+comment)
						unknowntype = False
					elif log_action == "protect" or log_action == "modify":
						isrecord and M.addRC_log_protect(change)

						print(user+" protect "+title+" comment:"+comment)
						message = M.link_user(user)+protectname[log_action]+M.link_page(title)+'（'+M.parse_wikicode(comment)+'）（'+M.parse_wikicode(change["log_params"]["description"])+'）'
						issend and M.sendmessage(message+message_append)
						unknowntype = False

				elif log_type == "newusers":
					isrecord and M.addRC_log_newusers(change)

					print(user+" newusers "+title)
					unknowntype = False
				elif log_type == "thanks":
					isrecord and M.addRC_log_thanks(change)
					unknowntype = False

				elif log_type == "patrol":
					isrecord and M.addRC_log_patrol(change)
					unknowntype = False

				elif log_type == "upload":
					isrecord and M.addRC_log_upload(change)
					unknowntype = False

				elif log_type == "rights":
					isrecord and M.addRC_log_rights(change)
					unknowntype = False

				elif log_type == "renameuser":
					isrecord and M.addRC_log_renameuser(change)
					unknowntype = False

				elif log_type == "merge":
					isrecord and M.addRC_log_merge(change)
					unknowntype = False

				elif log_type == "delete":
					if log_action == "delete":
						isrecord and M.addRC_log_delete(change)
						unknowntype = False

					elif log_action == "delete_redir":
						isrecord and M.addRC_log_delete(change)
						unknowntype = False

					elif log_action == "restore":
						isrecord and M.addRC_log_delete_restore(change)
						unknowntype = False

					elif log_action == "revision":
						isrecord and M.addRC_log_delete_revision(change)
						unknowntype = False

				elif log_type == "abusefilter":
					abusefiltername = {"hit": "觸發", "modify": "修改", "create": "建立"}

					if log_action == "hit":
						isrecord and M.addRC_log_abusefilter_hit(change)

						print(user+" hit af "+str(change["log_params"]["filter"])+" in "+title)
						unknowntype = False
					elif log_action == "modify" or log_action == "create":
						isrecord and M.addRC_log_abusefilter_modify(change)

						message = M.link_user(user)+abusefiltername[log_action]+M.link_abusefilter(change["log_params"]["newId"])+'（'+M.link_all('Special:Abusefilter/history/'+str(change["log_params"]["newId"])+'/diff/prev/'+str(change["log_params"]["historyId"]), '差異')+'）'

						if wiki in followwiki:
							issend = True
						if wiki in ["metawiki"]:
							issend = False

						issend and M.sendmessage(message+message_append)
						unknowntype = False
			
				elif log_type == "globalauth":
					if log_action == "setstatus":
						isrecord and M.addRC_log_globalauth(change)

						message = M.link_user(user)+'全域鎖定'+M.link_user(title[5:-7])+'（'+M.parse_wikicode(change["log_action_comment"])+'）'
						issend and M.sendmessage(message+message_append)
						unknowntype = False
			
				elif log_type == "gblblock":
					if log_action == "gblock2" or log_action == "modify":
						isrecord and M.addRC_log_gblblock(change)

						message = M.link_user(user)+'全域封禁'+M.link_user(title[5:-7])+'（'+M.parse_wikicode(change["log_action_comment"])+'）'
						issend and M.sendmessage(message+message_append)
						unknowntype = False
			
				elif log_type == "gblrename":
					if log_action == "rename":
						isrecord and M.addRC_log_gblrename(change)

						unknowntype = False
			
				elif log_type == "gblrights":
					if log_action == "usergroups":
						# ignore
						unknowntype = False
			
				elif log_type == "pagetranslation":
					if log_action == "associate":
						# ignore
						unknowntype = False
					elif log_action == "mark":
						# ignore
						unknowntype = False
					elif log_action == "deletelok":
						# ignore
						unknowntype = False
			
				elif log_type == "translationreview":
					if log_action == "group":
						# ignore
						unknowntype = False
					elif log_action == "message":
						# ignore
						unknowntype = False
			
				elif log_type == "review":
					if log_action == "approve-i":
						# ignore
						unknowntype = False
					elif log_action == "approve":
						# ignore
						unknowntype = False
					elif log_action == "unapprove":
						# ignore
						unknowntype = False
			
				elif log_type == "import":
					if log_action == "interwiki":
						# ignore
						unknowntype = False
			
				elif log_type == "tag":
					if log_action == "update":
						# ignore
						unknowntype = False
			
				elif log_type == "massmessage":
					if log_action == "send":
						# ignore
						unknowntype = False
					elif log_action == "skipoptout":
						# ignore
						unknowntype = False
			
			if unknowntype:
				M.log(json.dumps(change, ensure_ascii=False), logtype="unknowntype")

			if not isrecord:
				print(json.dumps(change, indent=4, sort_keys=True, ensure_ascii=False))

			if (wiki in followwiki and ctype in ["edit", "new"]) and change["namespace"] == 3 and re.match(r"^User talk:", title) and re.match(r"^(層級|层级)[234]", comment):
				reason = "被"+user+"警告："+comment
				M.addblack_user(title[10:], change["timestamp"], reason, msgprefix="自動")

		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			M.error(str(e)+" "+json.dumps(change))
			M.error(str(exc_type)+" "+str(fname)+" "+str(exc_tb.tb_lineno))
			print(e)
			print(exc_type, fname, exc_tb.tb_lineno)
