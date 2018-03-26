# -*- coding: utf-8 -*-
import json
from flask import Flask, request, abort
import re
import os
import sys
import cgi
from Monitor import Monitor

os.environ['TZ'] = 'UTC'

M = Monitor()

app = Flask(__name__)

@app.route("/")
def hello():
	return "Hello Wikimedia-RecentChange-Monitor!"

@app.route("/webhook", methods=['POST'])
def telegram():
	try:
		data = json.loads(request.data.decode("utf8"))
		if "message" in data:
			m_date = data["message"]["date"]
			m_chat_id = int(data["message"]["chat"]["id"])
			m_user_id = int(data["message"]["from"]["id"])
			m_first_name = data["message"]["from"]["first_name"]

			if "text" in data["message"] and m_chat_id in M.response_chat_id:
				M.chat_id = m_chat_id

				m_text = data["message"]["text"]
				M.log(m_text)

				if not m_text.startswith("/"):
					return "OK"

				def checkadmin():
					M.cur.execute("""SELECT * FROM `admin` WHERE `user_id` = %s""", (str(m_user_id)))
					rows = M.cur.fetchall()
					if len(rows) == 0:
						M.sendmessage("You are not an admin.")
						return False
					return True

				m = re.match(r"/setadmin", m_text)
				if m != None:
					if not checkadmin():
						return "OK"

					if "reply_to_message" not in data["message"]:
						M.sendmessage("You need to reply a message")
						return "OK"
					from_user_id = data["message"]["reply_to_message"]["from"]["id"]

					if from_user_id == m_user_id:
						M.sendmessage("You cannot set yourself as admin")
						return "OK"

					from_firstname = data["message"]["reply_to_message"]["from"]["first_name"]
					from_lastname = data["message"]["reply_to_message"]["from"]["last_name"]

					M.cur.execute("""INSERT INTO `admin` (`user_id`, `first_name`, `last_name`) VALUES (%s, %s, %s)""",
						(str(from_user_id), from_firstname, from_lastname) )
					M.db.commit()
					M.sendmessage("set "+from_firstname+" "+from_lastname+" ("+str(from_user_id)+") as an admin")
					return "OK"

				m = re.match(r"/deladmin", m_text)
				if m != None:
					if not checkadmin():
						return "OK"
						
					if "reply_to_message" not in data["message"]:
						M.sendmessage("You need to reply a message")
						return "OK"
					from_user_id = data["message"]["reply_to_message"]["from"]["id"]

					if from_user_id == m_user_id:
						M.sendmessage("You cannot revoke yourself")
						return "OK"

					from_firstname = data["message"]["reply_to_message"]["from"]["first_name"]
					from_lastname = data["message"]["reply_to_message"]["from"]["last_name"]

					M.cur.execute("""DELETE FROM `admin` WHERE `user_id` = %s""",
						(str(from_user_id)) )
					M.db.commit()
					M.sendmessage("revoke "+from_firstname+" "+from_lastname+" ("+str(from_user_id)+") as an admin")
					return "OK"

				m = re.match(r"/adduser\n(.+)(?:\n(.+))?", m_text)
				if m != None:
					if not checkadmin():
						return "OK"
						
					user, wiki = M.parse_user(m.group(1))
					reason = "add by "+m_first_name+": "+M.parse_reason(m.group(2))
					M.addblack_user(user, m_date, reason, wiki)
					return "OK"

				m = re.match(r"/addwhiteuser\n(.+)(?:\n(.+))?", m_text)
				if m != None:
					if not checkadmin():
						return "OK"
						
					user = m.group(1)
					reason = "add by "+m_first_name+": "+M.parse_reason(m.group(2))
					M.addwhite_user(user, m_date, reason)
					return "OK"

				m = re.match(r"/deluser\n(.+)(?:\n.+)?", m_text)
				if m != None:
					if not checkadmin():
						return "OK"
						
					user, wiki = M.parse_user(m.group(1))
					M.delblack_user(user, wiki)
					return "OK"

				m = re.match(r"/addpage\n(.+)(?:\n(.+))?", m_text)
				if m != None:
					if not checkadmin():
						return "OK"
						
					page, wiki = M.parse_page(m.group(1))
					reason = "add by "+m_first_name+": "+M.parse_reason(m.group(2))
					M.addblack_page(page, m_date, reason, wiki)
					return "OK"

				m = re.match(r"/massaddpage\n(.+(?:\n.+)*)\n(.+)", m_text)
				if m != None:
					if not checkadmin():
						return "OK"
					
					for pageline in m.group(1).split("\n"):
						page, wiki = M.parse_page(pageline)
						reason = "add by "+m_first_name+": "+M.parse_reason(m.group(2))
						M.addblack_page(page, m_date, reason, wiki)
					return "OK"

				m = re.match(r"/delpage\n(.+)(?:\n.+)?", m_text)
				if m != None:
					if not checkadmin():
						return "OK"
						
					page, wiki = M.parse_page(m.group(1))
					M.delblack_page(page, wiki)
					return "OK"

				m = re.match(r"/checkuser\n(.+)", m_text)
				if m != None:
					user, wiki = M.parse_user(m.group(1))

					message = ""
					rows = M.check_user_whitelist(user)
					if len(rows) != 0:
						message += "\non whitelist:"
						for record in rows:
							message += "\n"+cgi.escape(record[0], quote=False)+', '+M.formattimediff(record[1])

					rows = M.check_user_blacklist(user, wiki, ignorewhite=True)
					if len(rows) != 0:
						message += "\non blacklist:"
						for record in rows:
							message += "\n"+cgi.escape(record[0], quote=False)
							if record[2] != "":
								message += "("+record[2]+"@"+record[3]+")"
							else :
								message += "("+record[3]+")"
							message += ', '+M.formattimediff(record[1])

					if message != "":
						M.sendmessage(message)
					else :
						M.sendmessage("no result found")
					return "OK"

				m = re.match(r"/checkpage\n(.+)", m_text)
				if m != None:
					page, wiki = M.parse_page(m.group(1))

					message = ""
					rows = M.check_page_blacklist(page, wiki)
					if len(rows) != 0:
						message += "\non blacklist:"
						for record in rows:
							message += "\n"+cgi.escape(record[0], quote=False)+', '+M.formattimediff(record[1])

					if message != "":
						M.sendmessage(message)
					else :
						M.sendmessage("no result found")
					return "OK"

				m = re.match(r"/status", m_text)
				if m != None:
					message = "working"
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
