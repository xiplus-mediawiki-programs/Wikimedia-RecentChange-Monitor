# -*- coding: utf-8 -*-
import json
from flask import Flask, request, abort
import re
import os
import sys
import cgi
import pymysql
import traceback
from Monitor import Monitor

os.environ['TZ'] = 'UTC'

M = Monitor()

app = Flask(__name__)

@app.route("/")
def hello():
	html = ''
	html += '<form>'
	html += '<button type="submit" name="type" value="blackipv4">blackipv4</button>'
	html += '<button type="submit" name="type" value="blackipv6">blackipv6</button>'
	html += '<button type="submit" name="type" value="blackuser">blackuser</button>'
	html += '<button type="submit" name="type" value="blackpage">blackpage</button>'
	html += '</form>'
	if "type" in request.args:
		if request.args["type"] == "blackipv4":
			M.cur.execute("""SELECT `wiki`, `val`, `reason`, `timestamp` FROM `black_ipv4` ORDER BY `timestamp` DESC""")
			rows = M.cur.fetchall()
			html += '<table>'
			html += '<tr><th>wiki</th><th>ip</th><th>reason</th><th>timestamp</th></tr>'
			for row in rows:
				html += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (row[0], row[1], M.parse_wikicode(row[2]), M.formattimediff(row[3]))
			html += '</table>'
		elif request.args["type"] == "blackipv6":
			M.cur.execute("""SELECT `wiki`, `val`, `reason`, `timestamp` FROM `black_ipv6` ORDER BY `timestamp` DESC""")
			rows = M.cur.fetchall()
			html += '<table>'
			html += '<tr><th>wiki</th><th>ip</th><th>reason</th><th>timestamp</th></tr>'
			for row in rows:
				html += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (row[0], row[1], M.parse_wikicode(row[2]), M.formattimediff(row[3]))
			html += '</table>'
		elif request.args["type"] == "blackuser":
			M.cur.execute("""SELECT `wiki`, `user`, `reason`, `timestamp` FROM `black_user` ORDER BY `timestamp` DESC""")
			rows = M.cur.fetchall()
			html += '<table>'
			html += '<tr><th>wiki</th><th>user</th><th>reason</th><th>timestamp</th></tr>'
			for row in rows:
				html += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (row[0], row[1], M.parse_wikicode(row[2]), M.formattimediff(row[3]))
			html += '</table>'
		elif request.args["type"] == "whiteuser":
			M.cur.execute("""SELECT `user`, `reason`, `timestamp` FROM `white_user` ORDER BY `timestamp` DESC""")
			rows = M.cur.fetchall()
			html += '<table>'
			html += '<tr><th>user</th><th>reason</th><th>timestamp</th></tr>'
			for row in rows:
				html += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (row[0], M.parse_wikicode(row[1]), M.formattimediff(row[2]))
			html += '</table>'
		elif request.args["type"] == "blackpage":
			M.cur.execute("""SELECT `wiki`, `page`, `reason`, `timestamp` FROM `black_page` ORDER BY `timestamp` DESC""")
			rows = M.cur.fetchall()
			html += '<table>'
			html += '<tr><th>wiki</th><th>page</th><th>reason</th><th>timestamp</th></tr>'
			for row in rows:
				html += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (row[0], row[1], M.parse_wikicode(row[2]), M.formattimediff(row[3]))
			html += '</table>'
	return html

@app.route("/log")
def log():
	try:
		html = ""
		dbs = [
			'error',
			'log',
			'RC_142',
			'RC_categorize',
			'RC_edit',
			'RC_log_abusefilter_hit',
			'RC_log_abusefilter_modify',
			'RC_log_abuselog',
			'RC_log_block',
			'RC_log_delete',
			'RC_log_delete_restore',
			'RC_log_delete_revision',
			'RC_log_merge',
			'RC_log_move',
			'RC_log_newusers',
			'RC_log_patrol',
			'RC_log_protect',
			'RC_log_protect_move_prot',
			'RC_log_protect_unprotect',
			'RC_log_renameuser',
			'RC_log_rights',
			'RC_log_thanks',
			'RC_log_upload',
			'RC_new'
			]
		html += '<form>'
		for db in dbs:
			html += '<button type="submit" name="type" value="'+db+'">'+db+'</button> '
		html += '</form>'
		if "type" in request.args:
			logtype = request.args["type"]
			if logtype in dbs:
				M.cur2 = M.db.cursor(pymysql.cursors.DictCursor)
				M.cur2.execute("""SELECT * FROM """+logtype+""" ORDER BY `timestamp` DESC LIMIT 20""")
				rows = M.cur2.fetchall()
				if len(rows) == 0:
					html += 'No record'
				else:
					html += '<style>table{ border-collapse: collapse;} th, td{ vertical-align: top; border: 1px solid black; }</style>'
					html += '<table>'
					html += '<tr>'
					for col in rows[0]:
						if col == "parsedcomment":
							continue
						html += '<th>'+col+'</th>'
					html += '</tr>'
					for row in rows:
						html += '<tr>'
						for col in row:
							if col == "parsedcomment":
								continue
							elif (logtype == "error" and col == "error"):
								html += '<td><pre>'+cgi.escape(row[col], quote=False)+'</pre></td>'
							else:
								html += '<td>'+str(row[col])+'</td>'
						html += '</tr>'
					html += '</table>'
		return html
	except Exception as e:
		M.error(traceback.format_exc())
		return traceback.format_exc()

@app.route("/status")
def status():
	try:
		html = ""
		html += '<style>table{ border-collapse: collapse;} th, td{ vertical-align: top; border: 1px solid black; }</style>'
		html += '<table>'
		html += '<tr><th>database</th><th>last time</th></tr>'
		dbs = [
			'error',
			'log',
			'RC_142',
			'RC_categorize',
			'RC_edit',
			'RC_log_abusefilter_hit',
			'RC_log_abusefilter_modify',
			'RC_log_abuselog',
			'RC_log_block',
			'RC_log_delete',
			'RC_log_delete_restore',
			'RC_log_delete_revision',
			'RC_log_merge',
			'RC_log_move',
			'RC_log_newusers',
			'RC_log_patrol',
			'RC_log_protect',
			'RC_log_protect_move_prot',
			'RC_log_protect_unprotect',
			'RC_log_renameuser',
			'RC_log_rights',
			'RC_log_thanks',
			'RC_log_upload',
			'RC_new'
			]
		for db in dbs:
			M.cur.execute("""SELECT MAX(`timestamp`) FROM """+db)
			rows = M.cur.fetchall()
			if rows[0][0] == None:
				html += '<tr><td>%s</td><td>No record</td></tr>' % (db)
			else:
				html += '<tr><td><a href="{0}log?type={1}" target="_blank">{1}</td><td>{2}</td></tr>'.format(M.siteurl, db, M.formattimediff(rows[0][0]))
		html += '</table>'
		return html
	except Exception as e:
		M.error(traceback.format_exc())
		return "OK1"

@app.route("/webhook", methods=['POST'])
def telegram():
	try:
		data = json.loads(request.data.decode("utf8"))
		if "message" in data:
			m_date = data["message"]["date"]
			m_chat_id = int(data["message"]["chat"]["id"])
			m_user_id = int(data["message"]["from"]["id"])
			if "reply_to_message" in data["message"]:
				from_user_id = data["message"]["reply_to_message"]["from"]["id"]
				from_firstname = data["message"]["reply_to_message"]["from"]["first_name"]
				from_lastname = ""
				if "last_name" in data["message"]["reply_to_message"]["from"]:
					from_lastname = data["message"]["reply_to_message"]["from"]["last_name"]

			if "text" in data["message"] and m_chat_id in M.response_chat_id:
				M.chat_id = m_chat_id

				m_text = data["message"]["text"]
				M.log(m_text, logtype="request")

				if not m_text.startswith("/"):
					return "OK"

				def checkadmin():
					M.cur.execute("""SELECT `name` FROM `admin` WHERE `user_id` = %s""", (str(m_user_id)))
					rows = M.cur.fetchall()
					if len(rows) == 0:
						M.sendmessage("你沒有權限")
						return None
					return rows[0][0]

				m = re.match(r"/setadmin(?:@cvn_smart_bot)?(?:\s+(.+))?", m_text)
				if m != None:
					if not checkadmin():
						return "OK"

					if "reply_to_message" not in data["message"]:
						M.sendmessage("需要reply訊息")
						return "OK"

					name = from_firstname
					if m.group(1) != None and m.group(1).strip() != "":
						name = m.group(1)

					M.cur.execute("""REPLACE INTO `admin` (`user_id`, `name`) VALUES (%s, %s)""",
						(str(from_user_id), name) )
					M.db.commit()
					M.sendmessage("設定"+name+"("+(from_firstname+" "+from_lastname).strip()+")("+str(from_user_id)+")為管理員")
					return "OK"

				m = re.match(r"/deladmin", m_text)
				if m != None:
					if not checkadmin():
						return "OK"
						
					if "reply_to_message" not in data["message"]:
						M.sendmessage("需要reply訊息")
						return "OK"
					from_user_id = data["message"]["reply_to_message"]["from"]["id"]

					if from_user_id == m_user_id:
						M.sendmessage("你不能將自己除權")
						return "OK"

					count = M.cur.execute("""DELETE FROM `admin` WHERE `user_id` = %s""",
						(str(from_user_id)) )
					M.db.commit()
					if count == 0:
						M.sendmessage("該用戶不是管理員")
					else :
						M.sendmessage("移除"+(from_firstname+" "+from_lastname).strip()+"("+str(from_user_id)+")為管理員")
					return "OK"

				m = re.match(r"/(?:adduser|au)(?:@cvn_smart_bot)?\s+(.+)(?:\n(.+))?", m_text)
				if m != None:
					name = checkadmin()
					if name == None:
						return "OK"
						
					user, wiki = M.parse_user(m.group(1))
					reason = name+"加入："+M.parse_reason(m.group(2))
					M.addblack_user(user, m_date, reason, wiki)
					return "OK"

				m = re.match(r"/addwhiteuser(?:@cvn_smart_bot)?\s+(.+)(?:\n(.+))?", m_text)
				if m != None:
					name = checkadmin()
					if name == None:
						return "OK"
						
					user = m.group(1)
					reason = name+"加入："+M.parse_reason(m.group(2))
					M.addwhite_user(user, m_date, reason)
					return "OK"

				m = re.match(r"/delwhiteuser(?:@cvn_smart_bot)?\s+(.+)(?:\n.+)?", m_text)
				if m != None:
					if not checkadmin():
						return "OK"
						
					user = m.group(1)
					M.delwhite_user(user)
					return "OK"

				m = re.match(r"/(?:deluser|du)", m_text)
				if m != None:
					if not checkadmin():
						return "OK"

					m = re.match(r"/(?:deluser|du)(?:@cvn_smart_bot)?\s+(.+)(?:\n.+)?", m_text)
					if m != None:
						user, wiki = M.parse_user(m.group(1))
					elif "reply_to_message" in data["message"]:
						user = M.get_user_from_message_id(data["message"]["reply_to_message"]["message_id"])
						if len(user) == 0:
							M.sendmessage("無法從訊息找到所對應的對象")
							return "OK"
						else :
							user, wiki = M.parse_user(user[0][0])
					else :
						return "OK"
					
					M.delblack_user(user, wiki)
					return "OK"

				m = re.match(r"/setwiki", m_text)
				if m != None:
					if not checkadmin():
						return "OK"

					m = re.match(r"/(?:setwiki)(?:@cvn_smart_bot)?\s+(.+)?", m_text)
					if "reply_to_message" in data["message"]:
						user = M.get_user_from_message_id(data["message"]["reply_to_message"]["message_id"])
						if len(user) == 0:
							M.sendmessage("無法從訊息找到所對應的對象")
							return "OK"
						else :
							user, wiki = M.parse_user(user[0][0])
						wiki = m.group(1).strip()
					elif m != None:
						user, wiki = M.parse_user(m.group(1))
					M.setwikiblack_user(user, wiki)
					
					return "OK"

				m = re.match(r"/(?:addpage|ap)(?:@cvn_smart_bot)?\s+(.+)(?:\n(.+))?", m_text)
				if m != None:
					name = checkadmin()
					if name == None:
						return "OK"
						
					page, wiki = M.parse_page(m.group(1))
					reason = name+"加入："+M.parse_reason(m.group(2))
					M.addblack_page(page, m_date, reason, wiki)
					return "OK"

				m = re.match(r"/massaddpage(?:@cvn_smart_bot)?\s+(.+(?:\n.+)*)\n(.+)", m_text)
				if m != None:
					name = checkadmin()
					if name == None:
						return "OK"
					
					for pageline in m.group(1).split("\n"):
						page, wiki = M.parse_page(pageline)
						reason = name+"加入："+M.parse_reason(m.group(2))
						M.addblack_page(page, m_date, reason, wiki)
					return "OK"

				m = re.match(r"/(?:delpage|dp)(?:@cvn_smart_bot)?\s+(.+)(?:\n.+)?", m_text)
				if m != None:
					if not checkadmin():
						return "OK"
						
					page, wiki = M.parse_page(m.group(1))
					M.delblack_page(page, wiki)
					return "OK"

				m = re.match(r"/(?:checkuser|cu)", m_text)
				if m != None:
					m = re.match(r"/(?:checkuser|cu)(?:@cvn_smart_bot)?\s+(.+)", m_text)
					if m != None:
						user, wiki = M.parse_user(m.group(1))
					elif "reply_to_message" in data["message"]:
						user = M.get_user_from_message_id(data["message"]["reply_to_message"]["message_id"])
						if len(user) == 0:
							M.sendmessage("無法從訊息找到所對應的對象")
							return "OK"
						else :
							user, wiki = M.parse_user(user[0][0])
					else :
						return "OK"

					message = ""
					rows = M.check_user_whitelist(user)
					if len(rows) != 0:
						message += "\n於白名單："
						for record in rows:
							message += "\n"+M.parse_wikicode(record[0])+', '+M.formattimediff(record[1])

					rows = M.check_user_blacklist(user, wiki, ignorewhite=True)
					if len(rows) != 0:
						message += "\n於黑名單："
						for record in rows:
							message += "\n"+M.parse_wikicode(record[0])
							if record[2] != "":
								message += "("+record[2]+"@"+record[3]+")"
							else :
								message += "("+record[3]+")"
							message += ', '+M.formattimediff(record[1])

					if message != "":
						M.sendmessage(user+"@"+wiki+message)
					else :
						M.sendmessage(user+"@"+wiki+"：查無結果")
					return "OK"

				m = re.match(r"/(?:checkpage|cp)(?:@cvn_smart_bot)?\s+(.+)", m_text)
				if m != None:
					page, wiki = M.parse_page(m.group(1))

					message = ""
					rows = M.check_page_blacklist(page, wiki)
					if len(rows) != 0:
						message += "\n於黑名單："
						for record in rows:
							message += "\n"+M.parse_wikicode(record[0])+', '+M.formattimediff(record[1])

					if message != "":
						M.sendmessage(page+"@"+wiki+message)
					else :
						M.sendmessage(page+"@"+wiki+"：查無結果")
					return "OK"

				if re.match(r"/os(?:@cvn_smart_bot)?$", m_text) and "reply_to_message" in data["message"]:
					if not checkadmin():
						return "OK"

					M.deletemessage(data["message"]["message_id"])
					M.deletemessage(data["message"]["reply_to_message"]["message_id"])
					return "OK"

				if re.match(r"/osall(?:@cvn_smart_bot)?$", m_text) and "reply_to_message" in data["message"]:
					if not checkadmin():
						return "OK"

					M.deletemessage(data["message"]["message_id"])
					
					message_id = data["message"]["reply_to_message"]["message_id"]
					M.cur.execute("""SELECT `user` FROM `bot_message` WHERE `message_id` = %s""", (message_id))
					rows = M.cur.fetchall()
					if len(rows) == 0:
						M.sendmessage("無法從訊息找到所對應的對象")
						return "OK"
					user = rows[0][0]

					M.cur.execute("""SELECT `message_id` FROM `bot_message` WHERE `user` = %s""", (user))
					rows = M.cur.fetchall()
					for row in rows:
						M.deletemessage(row[0])

					M.sendmessage("已濫權掉"+str(len(rows))+"條訊息")
					return "OK"

				m = re.match(r"/status", m_text)
				if m != None:
					message = 'Webhook: <a href="https://zh.wikipedia.org/wiki/WORKING!!">WORKING!!</a>\n<a href="'+M.siteurl+'status">查看資料接收狀況</a>'
					M.sendmessage(message)
					return "OK"

		return "OK"

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		M.error(str(request.data.decode("utf8")))
		M.error(str(e))
		M.error(str(exc_type)+" "+str(fname)+" "+str(exc_tb.tb_lineno))
		return "OK"

if __name__ == "__main__":
	app.run()
