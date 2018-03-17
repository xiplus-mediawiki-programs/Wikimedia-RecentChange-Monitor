# -*- coding: utf-8 -*-
import json
from flask import Flask, request, abort
import re
import os
import sys
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

			if "text" in data["message"] and m_chat_id == M.chat_id:
				M.cur.execute("""SELECT * FROM `admin` WHERE `user_id` = %s""", (str(m_user_id)))
				rows = M.cur.fetchall()
				if len(rows) == 0:
					M.sendmessage("You are not an admin.")
					return "OK"

				m_text = data["message"]["text"]
				M.log(m_text)

				m = re.match(r"/setadmin", m_text)
				if m != None:
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
					user = m.group(1)
					M.log(user)
					M.log(str(user.split("|")))
					if "|" in user:
						wiki = user.split("|")[1]
						user = user.split("|")[0]
					else :
						wiki = M.wiki

					reason = "add by "+m_first_name
					if m.group(2) == None or m.group(2).strip() == "":
						reason += ": no reason"
					else :
						reason += ": "+m.group(2)
					M.addblack_user(user, m_date, reason, wiki)
					return "OK"

				m = re.match(r"/addwhiteuser\n(.+)(?:\n(.+))?", m_text)
				if m != None:
					user = m.group(1)
					reason = "add by "+m_first_name
					if m.group(2) == None or m.group(2).strip() == "":
						reason += ": no reason"
					else :
						reason += ": "+m.group(2)
					M.addwhite_user(user, m_date, reason)
					return "OK"

				m = re.match(r"/deluser\n(.+)(?:\n.+)?", m_text)
				if m != None:
					user = m.group(1)
					if "@" in user:
						wiki = user.split("@")[1]
						user = user.split("@")[0]
					else :
						wiki = M.wiki

					M.cur.execute("""DELETE FROM `black_user` WHERE `user` = %s AND `wiki` = %s""",
						(user, wiki) )
					M.db.commit()
					message = "deleted "+M.link_user(user)+"@"+wiki+" from user blacklist"
					M.sendmessage(message)
					return "OK"

				m = re.match(r"/addpage\n(.+)(?:\n(.+))?", m_text)
				if m != None:
					page = m.group(1)
					if "|" in page:
						wiki = page.split("|")[1]
						page = page.split("|")[0]
					else :
						wiki = M.wiki

					reason = "add by "+m_first_name
					if m.group(2) == None or m.group(2).strip() == "":
						reason += ": no reason"
					else :
						reason += ": "+m.group(2)
					M.cur.execute("""INSERT INTO `black_page` (`wiki`, `page`, `timestamp`, `reason`) VALUES (%s, %s, %s, %s)""",
						(wiki, page, m_date, reason) )
					M.db.commit()
					if wiki == M.wiki:
						message = "added "+M.link_page(page)+"("+wiki+") into watched page\nreason: "+reason
					else :
						message = "added "+page+"("+wiki+") into watched page\nreason: "+reason
					M.sendmessage(message)
					return "OK"

				m = re.match(r"/delpage\n(.+)(?:\n.+)?", m_text)
				if m != None:
					page = m.group(1)
					if "|" in page:
						wiki = page.split("|")[1]
						page = page.split("|")[0]
					else :
						wiki = M.wiki

					M.cur.execute("""DELETE FROM `black_page` WHERE `page` = %s AND `wiki` = %s""",
						(page, wiki) )
					M.db.commit()
					message = "deleted "+M.link_page(page)+"("+wiki+") from watched page"
					M.sendmessage(message)
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
		M.log(str(request.data.decode("utf8")))
		M.log(str(e))
		M.log(str(exc_type)+" "+str(fname)+" "+str(exc_tb.tb_lineno))
		return "OK"

if __name__ == "__main__":
	app.run()
