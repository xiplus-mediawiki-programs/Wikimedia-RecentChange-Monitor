# -*- coding: utf-8 -*-
import pymysql
import configparser
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import json
import cgi
import ipaddress
import re

class Monitor():
	def __init__(self):
		config = configparser.ConfigParser()
		configpath = os.path.dirname(os.path.realpath(__file__))+'/config.ini'
		config.read_file(open(configpath, encoding="utf8"))
		self.token = config.get('telegram', 'token')
		self.chat_id = config.getint('telegram', 'default_chat_id')
		self.response_chat_id = json.loads(config.get('telegram', 'response_chat_id'))
		self.db = pymysql.connect(host=config.get('database', 'host'),
								  user=config.get('database', 'user'),
								  passwd=config.get('database', 'passwd'),
								  db=config.get('database', 'db'),
								  charset=config.get('database', 'charset'))
		self.cur = self.db.cursor()
		self.defaultwiki = config.get('monitor', 'defaultwiki')
		self.wiki = config.get('monitor', 'defaultwiki')
		self.domain = config.get('monitor', 'defaultdomain')
		self.ipv4limit = config.getint('monitor', 'ipv4limit')
		self.ipv6limit = config.getint('monitor', 'ipv6limit')
		self.recordkept = config.getint('monitor', 'recordkept')

	def change_wiki_and_domain(self, wiki, domain):
		self.wiki = wiki
		self.domain = domain

	def addRC_edit(self, change):
		self.cur.execute("""INSERT INTO `RC_edit` (`bot`, `comment`, `id`, `length_new`, `length_old`, `minor`, `namespace`, `parsedcomment`, `revision_new`, `revision_old`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %r, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["length"]["new"], change["length"]["old"], change["minor"], change["namespace"], change["parsedcomment"], change["revision"]["new"], change["revision"]["old"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_142(self, change):
		self.cur.execute("""INSERT INTO `RC_142` (`bot`, `comment`, `id`, `namespace`, `parsedcomment`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["namespace"], change["parsedcomment"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_new(self, change):
		self.cur.execute("""INSERT INTO `RC_new` (`bot`, `comment`, `id`, `length_new`, `minor`, `namespace`, `parsedcomment`, `patrolled`, `revision_new`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %r, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["length"]["new"], change["minor"], change["namespace"], change["parsedcomment"], change["patrolled"], change["revision"]["new"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_categorize(self, change):
		self.cur.execute("""INSERT INTO `RC_categorize` (`bot`, `comment`, `id`, `namespace`, `parsedcomment`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["namespace"], change["parsedcomment"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_move(self, change):
		self.cur.execute("""INSERT INTO `RC_log_move` (`bot`, `comment`, `id`, `log_action`, `log_action_comment`, `log_id`, `log_params_noredir`, `log_params_target`, `namespace`, `parsedcomment`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["log_action"], change["log_action_comment"], change["log_id"], change["log_params"]["noredir"], change["log_params"]["target"], change["namespace"], change["parsedcomment"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_abusefilter_hit(self, change):
		self.cur.execute("""INSERT INTO `RC_log_abusefilter_hit` (`bot`, `log_action_comment`, `log_id`, `log_params_action`, `log_params_actions`, `log_params_filter`, `log_params_log`, `namespace`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["log_action_comment"], change["log_id"], change["log_params"]["action"], change["log_params"]["actions"], change["log_params"]["filter"], change["log_params"]["log"], change["namespace"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_abuselog(self, change):
		import dateutil.parser
		if change["filter_id"] == "":
			change["filter_id"] = "0"
		if "revid" not in change:
			change["revid"] = "0"
		elif change["revid"] == "":
			change["revid"] = "0"
		change["timestamp"] = str(int(dateutil.parser.parse(change["timestamp"]).timestamp()))
		self.cur.execute("""INSERT INTO `RC_log_abuselog` (`id`, `filter_id`, `filter`, `user`, `ns`, `revid`, `result`, `action`, `timestamp`, `title`, `wiki`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["id"], change["filter_id"], change["filter"], change["user"], change["ns"], change["revid"], change["result"], change["action"], change["timestamp"], change["title"], self.defaultwiki))
		self.db.commit()

	def addRC_log_abusefilter_modify(self, change):
		self.cur.execute("""INSERT INTO `RC_log_abusefilter_modify` (`bot`, `log_action_comment`, `log_id`, `log_params_historyId`, `log_params_newId`, `namespace`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["log_action_comment"], change["log_id"], change["log_params"]["historyId"], change["log_params"]["newId"], change["namespace"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_newusers(self, change):
		self.cur.execute("""INSERT INTO `RC_log_newusers` (`bot`, `comment`, `id`, `log_action`, `log_action_comment`, `log_id`, `log_params_userid`, `namespace`, `parsedcomment`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["log_action"], change["log_action_comment"], change["log_id"], change["log_params"]["userid"], change["namespace"], change["parsedcomment"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_block(self, change):
		self.cur.execute("""INSERT INTO `RC_log_block` (`bot`, `comment`, `id`, `log_action`, `log_action_comment`, `log_id`, `log_params_flags`, `log_params_duration`, `namespace`, `parsedcomment`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["log_action"], change["log_action_comment"], change["log_id"], change["log_params"]["flags"], change["log_params"]["duration"], change["namespace"], change["parsedcomment"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_block_unblock(self, change):
		self.cur.execute("""INSERT INTO `RC_log_block` (`bot`, `comment`, `id`, `log_action`, `log_action_comment`, `log_id`, `log_params_flags`, `log_params_duration`, `namespace`, `parsedcomment`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["log_action"], change["log_action_comment"], change["log_id"], "", "", change["namespace"], change["parsedcomment"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_upload(self, change):
		self.cur.execute("""INSERT INTO `RC_log_upload` (`bot`, `comment`, `id`, `log_action`, `log_action_comment`, `log_id`, `log_params_img_timestamp`, `log_params_img_sha1`, `namespace`, `parsedcomment`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["log_action"], change["log_action_comment"], change["log_id"], change["log_params"]["img_timestamp"], change["log_params"]["img_sha1"], change["namespace"], change["parsedcomment"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_protect(self, change):
		self.cur.execute("""INSERT INTO `RC_log_protect` (`bot`, `comment`, `id`, `log_action`, `log_action_comment`, `log_id`, `log_params_details`, `log_params_description`, `log_params_cascade`, `namespace`, `parsedcomment`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %r, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["log_action"], change["log_action_comment"], change["log_id"], json.dumps(change["log_params"]["details"]), change["log_params"]["description"], change["log_params"]["cascade"], change["namespace"], change["parsedcomment"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_protect_unprotect(self, change):
		self.cur.execute("""INSERT INTO `RC_log_protect_unprotect` (`bot`, `comment`, `id`, `log_action`, `log_action_comment`, `log_id`, `namespace`, `parsedcomment`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %r, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["log_action"], change["log_action_comment"], change["log_id"], change["namespace"], change["parsedcomment"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_protect_move_prot(self, change):
		self.cur.execute("""INSERT INTO `RC_log_protect_move_prot` (`bot`, `comment`, `id`, `log_action`, `log_action_comment`, `log_id`, `log_params_oldtitle`, `namespace`, `parsedcomment`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %r, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["log_action"], change["log_action_comment"], change["log_id"], change["log_params"]["oldtitle"], change["namespace"], change["parsedcomment"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_renameuser(self, change):
		self.cur.execute("""INSERT INTO `RC_log_renameuser` (`bot`, `comment`, `id`, `log_action`, `log_action_comment`, `log_id`, `log_params_olduser`, `log_params_newuser`, `log_params_edits`, `namespace`, `parsedcomment`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["log_action"], change["log_action_comment"], change["log_id"], change["log_params"]["olduser"], change["log_params"]["newuser"], change["log_params"]["edits"], change["namespace"], change["parsedcomment"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_merge(self, change):
		self.cur.execute("""INSERT INTO `RC_log_merge` (`bot`, `comment`, `id`, `log_action`, `log_action_comment`, `log_id`, `log_params_dest`, `log_params_mergepoint`, `namespace`, `parsedcomment`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["log_action"], change["log_action_comment"], change["log_id"], change["log_params"]["dest"], change["log_params"]["mergepoint"], change["namespace"], change["parsedcomment"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_rights(self, change):
		self.cur.execute("""INSERT INTO `RC_log_rights` (`bot`, `comment`, `id`, `log_action`, `log_action_comment`, `log_id`, `log_params_newgroups`, `log_params_oldgroups`, `log_params_newmetadata`, `log_params_oldmetadata`, `namespace`, `parsedcomment`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["log_action"], change["log_action_comment"], change["log_id"], json.dumps(change["log_params"]["newgroups"]), json.dumps(change["log_params"]["oldgroups"]), json.dumps(change["log_params"]["newmetadata"]), json.dumps(change["log_params"]["oldmetadata"]), change["namespace"], change["parsedcomment"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_patrol(self, change):
		self.cur.execute("""INSERT INTO `RC_log_patrol` (`bot`, `log_action`, `log_action_comment`, `log_id`, `log_params_auto`, `log_params_previd`, `log_params_curid`, `namespace`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %r, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["log_action"], change["log_action_comment"], change["log_id"], change["log_params"]["auto"], change["log_params"]["previd"], change["log_params"]["curid"], change["namespace"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_thanks(self, change):
		self.cur.execute("""INSERT INTO `RC_log_thanks` (`bot`, `log_action`, `log_action_comment`, `log_id`, `namespace`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["log_action"], change["log_action_comment"], change["log_id"], change["namespace"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_delete(self, change):
		self.cur.execute("""INSERT INTO `RC_log_delete` (`bot`, `comment`, `id`, `log_action`, `log_action_comment`, `log_id`, `namespace`, `parsedcomment`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["log_action"], change["log_action_comment"], change["log_id"], change["namespace"], change["parsedcomment"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_delete_restore(self, change):
		self.cur.execute("""INSERT INTO `RC_log_delete_restore` (`bot`, `comment`, `id`, `log_action_comment`, `log_id`, `log_params_count_files`, `log_params_count_revisions`, `namespace`, `parsedcomment`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["log_action_comment"], change["log_id"], change["log_params"]["count"]["files"], change["log_params"]["count"]["revisions"], change["namespace"], change["parsedcomment"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addRC_log_delete_revision(self, change):
		self.cur.execute("""INSERT INTO `RC_log_delete_revision` (`bot`, `comment`, `id`, `log_action_comment`, `log_id`, `log_params_ids`, `log_params_type`, `log_params_nfield`, `log_params_ofield`, `namespace`, `parsedcomment`, `timestamp`, `title`, `user`, `wiki`) VALUES (%r, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (change["bot"], change["comment"], change["id"], change["log_action_comment"], change["log_id"], json.dumps(change["log_params"]["ids"]), change["log_params"]["type"], change["log_params"]["nfield"], change["log_params"]["ofield"], change["namespace"], change["parsedcomment"], change["timestamp"], change["title"], change["user"], change["wiki"]))
		self.db.commit()

	def addblack_user(self, user, timestamp, reason, wiki=None, msgprefix=""):
		if wiki == None:
			wiki = self.wiki
		user = user.strip()
		wiki = wiki.strip()

		userobj = self.user_type(user)
		if type(userobj) == User:
			self.cur.execute("""INSERT INTO `black_user` (`wiki`, `user`, `timestamp`, `reason`) VALUES (%s, %s, %s, %s)""",
				(wiki, userobj.user, str(timestamp), reason) )
			self.db.commit()
			self.sendmessage(msgprefix+"added User:"+self.link_user(userobj.user, wiki)+"@"+wiki+" into user blacklist\nreason: "+cgi.escape(reason, quote=False))
			return
		elif type(userobj) == IPv4:
			if int(userobj.end) - int(userobj.start) > self.ipv4limit:
				self.sendmessage("IP數量超過上限")
				return
			self.cur.execute("""INSERT INTO `black_ipv4` (`wiki`, `val`, `start`, `end`, `timestamp`, `reason`) VALUES (%s, %s, %s, %s, %s, %s)""",
				(wiki, str(userobj.val), str(int(userobj.start)), str(int(userobj.end)), str(timestamp), reason) )
			self.db.commit()
		elif type(userobj) == IPv6:
			if int(userobj.end) - int(userobj.start) > self.ipv6limit:
				self.sendmessage("IP數量超過上限")
				return
			self.cur.execute("""INSERT INTO `black_ipv6` (`wiki`, `val`, `start`, `end`, `timestamp`, `reason`) VALUES (%s, %s, %s, %s, %s, %s)""",
				(wiki, str(userobj.val), str(int(userobj.start)), str(int(userobj.end)), str(timestamp), reason) )
			self.db.commit()
		else:
			self.error("cannot detect user type: "+user)
			return
		if type(userobj) in [IPv4, IPv6]:
			if userobj.start == userobj.end:
				self.sendmessage(msgprefix+"added IP:"+self.link_user(str(userobj.start), wiki)+"@"+wiki+" into user blacklist\nreason: "+cgi.escape(reason, quote=False))
			elif userobj.type == "CIDR":
				self.sendmessage(msgprefix+"added IP:"+self.link_user(str(userobj.val), wiki)+"@"+wiki+" into user blacklist\nreason: "+cgi.escape(reason, quote=False))
			elif userobj.type == "range":
				self.sendmessage(msgprefix+"added IP:"+str(userobj.start)+"-"+str(userobj.end)+"@"+wiki+" into user blacklist\nreason: "+cgi.escape(reason, quote=False))

	def delblack_user(self, user, wiki=None, msgprefix=""):
		if wiki == None:
			wiki = self.wiki
		user = user.strip()
		wiki = wiki.strip()

		userobj = self.user_type(user)
		if type(userobj) == User:
			count = self.cur.execute("""DELETE FROM `black_user` WHERE `user` = %s AND `wiki` = %s""",
				(userobj.user, wiki) )
			self.db.commit()
			self.sendmessage(str(count)+" records about User:"+self.link_user(userobj.user, wiki)+"("+wiki+") deleted from user blacklist")
			return
		elif type(userobj) == IPv4:
			count = self.cur.execute("""DELETE FROM `black_ipv4` WHERE `start` = %s AND `end` = %s AND `wiki` = %s""",
				(str(int(userobj.start)), str(int(userobj.end)), wiki) )
			self.db.commit()
		elif type(userobj) == IPv6:
			count = self.cur.execute("""DELETE FROM `black_ipv6` WHERE `start` = %s AND `end` = %s AND `wiki` = %s""",
				(str(int(userobj.start)), str(int(userobj.end)), wiki) )
			self.db.commit()
		else:
			self.error("cannot detect user type: "+user)
			return
		if type(userobj) in [IPv4, IPv6]:
			if userobj.start == userobj.end:
				self.sendmessage(msgprefix+str(count)+" records about IP:"+self.link_user(str(userobj.start), wiki)+"@"+wiki+" deleted from user blacklist")
			elif userobj.type == "CIDR":
				self.sendmessage(msgprefix+str(count)+" records about IP:"+self.link_user(str(userobj.val), wiki)+"@"+wiki+" deleted from user blacklist")
			elif userobj.type == "range":
				self.sendmessage(msgprefix+str(count)+" records about IP:"+str(userobj.start)+"-"+str(userobj.end)+"@"+wiki+" deleted from user blacklist")

	def addwhite_user(self, user, timestamp, reason, msgprefix=""):
		user = user.strip()
		self.cur.execute("""INSERT INTO `white_user` (`user`, `timestamp`, `reason`) VALUES (%s, %s, %s)""",
			(user, timestamp, reason) )
		self.db.commit()
		self.sendmessage(msgprefix+"added "+self.link_user(user, "")+"@global into user whitelist\nreason: "+cgi.escape(reason, quote=False))

	def check_user_blacklist(self, user, wiki=None, ignorewhite=False):
		if wiki == None:
			wiki = self.wiki
		user = user.strip()
		wiki = wiki.strip()

		if not ignorewhite:
			rows = self.check_user_whitelist(user, wiki)
			if len(rows) != 0:
				return []

		userobj = self.user_type(user)
		if type(userobj) == User:
			self.cur.execute("""SELECT `reason`, `timestamp`, '' AS `val`, `wiki` FROM `black_user` WHERE `user` = %s AND (`wiki` = %s OR `wiki` = 'global') ORDER BY `timestamp` DESC""", (user, wiki))
			return self.cur.fetchall()
		elif type(userobj) == IPv4:
			self.cur.execute("""SELECT `reason`, `timestamp`, `val`, `wiki` FROM `black_ipv4` WHERE `start` <= %s AND  `end` >= %s AND (`wiki` = %s OR `wiki` = 'global') ORDER BY `timestamp` DESC""",
				(str(int(userobj.start)), str(int(userobj.end)), wiki) )
			return self.cur.fetchall()
		elif type(userobj) == IPv6:
			self.cur.execute("""SELECT `reason`, `timestamp`, `val`, `wiki` FROM `black_ipv6` WHERE `start` <= %s AND  `end` >= %s AND (`wiki` = %s OR `wiki` = 'global') ORDER BY `timestamp` DESC""",
				(str(int(userobj.start)), str(int(userobj.end)), wiki) )
			return self.cur.fetchall()
		else:
			self.error("cannot detect user type: "+user)
			return []

	def check_user_blacklist_with_reason(self, user, reason, wiki=None, ignorewhite=False):
		if wiki == None:
			wiki = self.wiki
		user = user.strip()

		if not ignorewhite:
			rows = self.check_user_whitelist(user, wiki)
			if len(rows) != 0:
				return []

		userobj = self.user_type(user)
		if type(userobj) == User:
			self.cur.execute("""SELECT `reason`, `timestamp`, `user` FROM `black_user` WHERE `user` = %s AND `reason` = %s AND (`wiki` = %s OR `wiki` = 'global') ORDER BY `timestamp` DESC""", (user, reason, wiki))
			return self.cur.fetchall()
		elif type(userobj) == IPv4:
			self.cur.execute("""SELECT `reason`, `timestamp`, `val` FROM `black_ipv4` WHERE `start` <= %s AND  `end` >= %s AND `reason` = %s AND (`wiki` = %s OR `wiki` = 'global') ORDER BY `timestamp` DESC""",
				(str(int(userobj.start)), str(int(userobj.end)), reason, wiki) )
			return self.cur.fetchall()
		elif type(userobj) == IPv6:
			self.cur.execute("""SELECT `reason`, `timestamp`, `val` FROM `black_ipv6` WHERE `start` <= %s AND  `end` >= %s AND `reason` = %s AND (`wiki` = %s OR `wiki` = 'global') ORDER BY `timestamp` DESC""",
				(str(int(userobj.start)), str(int(userobj.end)), reason, wiki) )
			return self.cur.fetchall()
		else:
			self.error("cannot detect user type: "+user)
			return []

	def check_user_whitelist(self, user, wiki=None):
		if wiki == None:
			wiki = self.wiki
		user = user.strip()
		wiki = wiki.strip()

		self.cur.execute("""SELECT `reason`, `timestamp` FROM `white_user` WHERE `user` = %s ORDER BY `timestamp` DESC""", (user))
		return self.cur.fetchall()

	def addblack_page(self, page, timestamp, reason, wiki=None, msgprefix=""):
		if wiki == None:
			wiki = self.wiki
		page = page.strip()
		wiki = wiki.strip()

		self.cur.execute("""INSERT INTO `black_page` (`wiki`, `page`, `timestamp`, `reason`) VALUES (%s, %s, %s, %s)""",
			(wiki, page, timestamp, reason) )
		self.db.commit()
		self.sendmessage("added "+self.link_page(page, wiki)+"("+wiki+") into watched page\nreason: "+reason)

	def delblack_page(self, page, wiki=None, msgprefix=""):
		if wiki == None:
			wiki = self.wiki
		page = page.strip()
		wiki = wiki.strip()

		count = self.cur.execute("""DELETE FROM `black_page` WHERE `page` = %s AND `wiki` = %s""",
			(page, wiki) )
		self.db.commit()
		self.sendmessage(str(count)+" records about "+self.link_page(page, wiki)+"("+wiki+") deleted from watched page")

	def check_page_blacklist(self, page, wiki=None):
		if wiki == None:
			wiki = self.wiki
		page = page.strip()
		wiki = wiki.strip()
		self.cur.execute("""SELECT `reason`, `timestamp` FROM `black_page` WHERE `page` = %s AND `wiki` = %s ORDER BY `timestamp` DESC""", (page, wiki))
		return self.cur.fetchall()

	def link_all(self, page, text=None, wiki=None):
		if text == None:
			text = page
		if wiki != None and wiki != self.wiki:
			return page
		return '<a href="https://'+self.domain+'/wiki/'+urllib.parse.quote(page)+'">'+text+'</a>'

	def link_user(self, user, wiki=None):
		if wiki != None and wiki != self.wiki:
			return user
		return '<a href="https://'+self.domain+'/wiki/Special:Contributions/'+urllib.parse.quote(user)+'">'+user+'</a>'

	def link_page(self, title, wiki=None):
		if wiki != None and wiki != self.wiki:
			return title
		return '<a href="https://'+self.domain+'/wiki/'+urllib.parse.quote(title)+'">'+title+'</a>'

	def link_diff(self, id):
		return '<a href="https://'+self.domain+'/wiki/Special:Diff/'+str(id)+'">diff</a>'

	def link_abusefilter(self, id):
		if id == "":
			return "AF"
		return '<a href="https://'+self.domain+'/wiki/Special:Abusefilter/'+str(id)+'">AF '+str(id)+'</a>'

	def link_abuselog(self, id):
		return '<a href="https://'+self.domain+'/wiki/Special:Abuselog/'+str(id)+'">detail</a>'

	def sendmessage(self, message):
		try:
			self.log(message)
			url = "https://api.telegram.org/bot"+self.token+"/sendMessage?chat_id="+str(self.chat_id)+"&parse_mode=HTML&disable_web_page_preview=1&text="+urllib.parse.quote_plus(message.encode())
			res = urllib.request.urlopen(url).read().decode("utf8")
		except urllib.error.HTTPError as e:
			self.error("send message error:"+str(e.code)+" "+str(e.read().decode("utf-8"))+" message: "+message)

	def log(self, log, timestamp=None):
		if timestamp == None:
			timestamp = int(time.time())
		self.cur.execute("""INSERT INTO `log` (`timestamp`, `log`) VALUES (%s, %s)""",
			(timestamp, str(log)) )
		self.db.commit()

	def error(self, error, timestamp=None):
		if timestamp == None:
			timestamp = int(time.time())
		self.cur.execute("""INSERT INTO `error` (`timestamp`, `error`) VALUES (%s, %s)""",
			(timestamp, str(error)) )
		self.db.commit()

	def formattimediff(self, timestamp, basetime = None):
		if basetime == None:
			basetime = int(time.time())
		diff = abs(int(timestamp) - basetime)
		if diff < 60:
			return str(diff)+" secs"
		if diff < 60*60:
			return str(int(diff/60))+" mins"
		if diff < 60*60*24:
			return str(int(diff/60/60))+" hrs"
		return str(int(diff/60/60/24))+" days"
	
	def parse_user(self, user, delimiter="|"):
		if delimiter in user:
			wiki = user.split(delimiter)[1]
			user = user.split(delimiter)[0]
		else :
			wiki = self.wiki
		return user, wiki

	def parse_page(self, page, delimiter="|"):
		if delimiter in page:
			wiki = page.split(delimiter)[1]
			page = page.split(delimiter)[0]
		else :
			wiki = self.wiki
		return page, wiki

	def parse_reason(self, reason):
		if reason == None or reason.strip() == "":
			return "no reason"
		else :
			return reason

	def user_type(self, user):
		try:
			user = user.strip()
			m = re.match(r"(.+)\-(.+)", user)
			if m != None:
				ip1 = ipaddress.ip_address(m.group(1))
				ip2 = ipaddress.ip_address(m.group(2))
				if ip1 > ip2:
					ip1, ip2 = ip2, ip1
				if type(ip1) == type(ip2):
					if type(ip1) == ipaddress.IPv4Address:
						return IPv4(ip1, ip2, "range", user)
					elif type(ip1) == ipaddress.IPv6Address:
						return IPv6(ip1, ip2, "range", user)
				self.error("cannot detect user type: "+user)
				raise ValueError
			network = ipaddress.ip_network(user, strict=False)
			if type(network) == ipaddress.IPv4Network:
				if network[0] == network[-1]:
					return IPv4(network[0], network[-1], "CIDR", network[0])
				else :
					return IPv4(network[0], network[-1], "CIDR", network)
			elif type(network) == ipaddress.IPv6Network:
				if network[0] == network[-1]:
					return IPv6(network[0], network[-1], "CIDR", network[0])
				else :
					return IPv6(network[0], network[-1], "CIDR", network)
			else :
				self.error("cannot detect user type: "+user)
				raise ValueError
		except ValueError as e:
			return User(user)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			self.error(str(e))
			self.error(str(exc_type)+" "+str(fname)+" "+str(exc_tb.tb_lineno))
			return None

	def __exit__(self):
		self.db.close()

class User():
	def __init__(self, user):
		self.user = user

class IPv4():
	def __init__(self, start, end, type, val):
		self.start = start
		self.end = end
		self.type = type
		self.val = val

class IPv6():
	def __init__(self, start, end, type, val):
		self.start = start
		self.end = end
		self.type = type
		self.val = val
