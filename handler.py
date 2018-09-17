# -*- coding: utf-8 -*-
import json
from flask import Flask, request, abort, send_file
from flask_cors import CORS
import re
import os
import cgi
import pymysql
import traceback
import time
from Monitor import Monitor

os.environ['TZ'] = 'UTC'

M = Monitor()

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello():
    html = """
        <a href="./status">status</a>
        <a href="./log?type=log">log</a>
        blacklist
        <form>
            <button type="submit" name="type" value="blackipv4">
                blackipv4</button>
            <button type="submit" name="type" value="blackipv6">
                blackipv6</button>
            <button type="submit" name="type" value="blackuser">
                blackuser</button>
            <button type="submit" name="type" value="blackpage">
                blackpage</button>
        </form>
        """
    if "type" in request.args:
        if request.args["type"] == "blackipv4":
            M.cur.execute(
                """SELECT `wiki`, `val`, `point`, `reason`, `black_ipv4`.`timestamp`
                   FROM `black_ipv4` 
                   LEFT JOIN `user_score`
                   ON `black_ipv4`.`userhash` = `user_score`.`userhash`
                   WHERE `point` != 0
                   ORDER BY `black_ipv4`.`timestamp` DESC""")
            rows = M.cur.fetchall()
            html += """
                <table>
                <tr>
                    <th>wiki</th>
                    <th>ip</th>
                    <th>point</th>
                    <th>reason</th>
                    <th>timestamp</th>
                </tr>
                """
            for row in rows:
                html += """
                    <tr>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                    </tr>
                    """.format(row[0],
                               row[1],
                               row[2],
                               M.parse_wikicode(row[3]),
                               M.formattimediff(row[4]))
            html += """</table>"""
        elif request.args["type"] == "blackipv6":
            M.cur.execute(
                """SELECT `wiki`, `val`, `point`, `reason`, `black_ipv6`.`timestamp`
                   FROM `black_ipv6`
                   LEFT JOIN `user_score`
                   ON `black_ipv6`.`userhash` = `user_score`.`userhash`
                   WHERE `point` != 0
                   ORDER BY `black_ipv6`.`timestamp` DESC""")
            rows = M.cur.fetchall()
            html += """<table>"""
            html += """
                <tr>
                    <th>wiki</th>
                    <th>ip</th>
                    <th>point</th>
                    <th>reason</th>
                    <th>timestamp</th>
                </tr>
                """
            for row in rows:
                html += """
                    <tr>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                    </tr>
                    """.format(row[0],
                               row[1],
                               row[2],
                               M.parse_wikicode(row[3]),
                               M.formattimediff(row[4]))
            html += """</table>"""
        elif request.args["type"] == "blackuser":
            M.cur.execute(
                """SELECT `wiki`, `user`, `point`, `reason`, `black_user`.`timestamp`
                   FROM `black_user`
                   LEFT JOIN `user_score`
                   ON `black_user`.`userhash` = `user_score`.`userhash`
                   WHERE `point` != 0
                   ORDER BY `black_user`.`timestamp` DESC""")
            rows = M.cur.fetchall()
            html += """<table>"""
            html += """
                <tr>
                    <th>wiki</th>
                    <th>user</th>
                    <th>point</th>
                    <th>reason</th>
                    <th>timestamp</th>
                </tr>
                """
            for row in rows:
                html += """
                    <tr>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                    </tr>
                    """.format(row[0],
                               row[1],
                               row[2],
                               M.parse_wikicode(row[3]),
                               M.formattimediff(row[4]))
            html += """</table>"""
        elif request.args["type"] == "whiteuser":
            M.cur.execute(
                """SELECT `user`, `point`, `reason`, `white_user`.`timestamp`
                   FROM `white_user`
                   LEFT JOIN `user_score`
                   ON `white_user`.`userhash` = `user_score`.`userhash`
                   WHERE `point` != 0
                   ORDER BY `white_user`.`timestamp` DESC""")
            rows = M.cur.fetchall()
            html += """<table>"""
            html += """
                <tr>
                    <th>user</th>
                    <th>point</th>
                    <th>reason</th>
                    <th>timestamp</th>
                </tr>
                """
            for row in rows:
                html += """
                    <tr>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                    </tr>
                    """.format(row[0],
                               row[1],
                               M.parse_wikicode(row[2]),
                               M.formattimediff(row[3]))
            html += """</table>"""
        elif request.args["type"] == "blackpage":
            M.cur.execute("""SELECT `wiki`, `page`, `reason`, `timestamp`
                             FROM `black_page` ORDER BY `timestamp` DESC""")
            rows = M.cur.fetchall()
            html += """<table>"""
            html += """
                <tr>
                    <th>wiki</th>
                    <th>page</th>
                    <th>reason</th>
                    <th>timestamp</th>
                </tr>
                """
            for row in rows:
                html += """
                    <tr>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                    </tr>
                    """.format(row[0],
                               row[1],
                               M.parse_wikicode(row[2]),
                               M.formattimediff(row[3]))
            html += """</table>"""
    return html


@app.route("/log")
def log():
    try:
        html = """
            <a href="./status">status</a>
            log
            <a href="./">blacklist</a>
            <form>
            """
        dbs = [
            'bot_message',
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
            html += ('<button type="submit" name="type" value="{0}">' +
                     '{0}</button> ').format(db)
        html += '</form>'
        if "type" in request.args:
            logtype = request.args["type"]
            if logtype in dbs:
                M.cur2 = M.db.cursor(pymysql.cursors.DictCursor)
                M.cur2.execute(
                    """SELECT * FROM {} ORDER BY `timestamp` DESC LIMIT 20"""
                    .format(logtype)
                    )
                rows = M.cur2.fetchall()
                if len(rows) == 0:
                    html += 'No record'
                else:
                    html += """
                        <style>
                        table {
                            border-collapse: collapse;
                        }
                        th, td {
                            vertical-align: top;
                            border: 1px solid black;
                        }
                        </style>
                        """
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
                                html += ('<td><pre>' +
                                         cgi.escape(row[col], quote=False) +
                                         '</pre></td>')
                            elif (col == "log_action_comment"
                                  or col == "comment"):
                                html += ('<td>' +
                                         cgi.escape(row[col], quote=False) +
                                         '</pre>')
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
        html = """
        <style>
            table {
                border-collapse: collapse;
            }
            th, td {
                vertical-align: top;
                border: 1px solid black;
            }
        </style>
        status
        <a href="./log?type=log">log</a>
        <a href="./">blacklist</a>
        <table>
        <tr>
            <th>database</th>
            <th>last time</th>
        </tr>
        """
        dbs = [
            'bot_message',
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
            if rows[0][0] is None:
                html += """
                    <tr>
                        <td>{}</td>
                        <td>No record</td>
                    </tr>
                    """.format(db)
            else:
                html += """
                    <tr>
                        <td><a href="{0}log?type={1}" target="_blank">{1}</td>
                        <td>{2}</td>
                    </tr>
                    """.format(M.siteurl, db, M.formattimediff(rows[0][0]))
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
                reply_from = data["message"]["reply_to_message"]["from"]
                from_user_id = reply_from["id"]
                from_firstname = reply_from["first_name"]
                from_lastname = ""
                if "last_name" in reply_from:
                    from_lastname = reply_from["last_name"]

            if "text" in data["message"]:

                M.chat_id = m_chat_id

                m_text = data["message"]["text"]
                M.log(m_text, logtype="request")

                if not m_text.startswith("/"):
                    return "OK"

                def checkadmin():
                    M.cur.execute(
                        """SELECT `name` FROM `admin` WHERE `user_id` = %s""",
                        (str(m_user_id))
                    )
                    rows = M.cur.fetchall()
                    if len(rows) == 0:
                        M.sendmessage("你沒有權限")
                        return None
                    return rows[0][0]

                m = re.match(r"/gettoken(?:@cvn_smart_bot)?",
                             m_text)
                if m_chat_id == m_user_id and m is not None:
                    if not checkadmin():
                        return "OK"

                    M.cur.execute(
                        """SELECT `token` FROM `admin` WHERE `user_id` = %s""",
                        (str(m_user_id))
                    )
                    rows = M.cur.fetchall()
                    if len(rows) > 0:
                        M.sendmessage(
                            "您的存取權杖是\ncvn_smart(" + rows[0][0]
                            + ")\n使用 /newtoken 取得新的",
                            nolog=True)
                    else:
                        M.sendmessage(
                            "查詢存取權杖失敗，使用 /newtoken 取得新的",
                            nolog=True)

                    return "OK"

                m = re.match(r"/newtoken(?:@cvn_smart_bot)?",
                             m_text)
                if m_chat_id == m_user_id and m is not None:
                    if not checkadmin():
                        return "OK"

                    import random
                    import string

                    token = ''.join(
                        random.choice(string.ascii_lowercase + string.digits)
                        for _ in range(32))
                    M.cur.execute(
                        """UPDATE `admin` SET `token` = %s
                        WHERE `user_id` = %s""",
                        (token, m_user_id)
                    )
                    M.db.commit()
                    M.sendmessage(
                        "您的存取權杖是\ncvn_smart(" + token
                        + ")\n舊的存取權杖已失效",
                        nolog=True)
                    return "OK"

                if m_chat_id not in M.response_chat_id:
                    return "OK"

                m = re.match(r"/setadmin(?:@cvn_smart_bot)?(?:\s+(.+))?",
                             m_text)
                if m is not None:
                    if not checkadmin():
                        return "OK"

                    if "reply_to_message" not in data["message"]:
                        M.sendmessage("需要reply訊息")
                        return "OK"

                    name = from_firstname
                    if m.group(1) is not None and m.group(1).strip() != "":
                        name = m.group(1)

                    M.cur.execute("""REPLACE INTO `admin` (`user_id`, `name`)
                                     VALUES (%s, %s)""",
                                  (str(from_user_id), name))
                    M.db.commit()
                    M.sendmessage(
                        "設定" + name + "(" +
                        (from_firstname + " " + from_lastname).strip() +
                        ")(" + str(from_user_id) + ")為管理員"
                    )
                    return "OK"

                m = re.match(r"/deladmin", m_text)
                if m is not None:
                    if not checkadmin():
                        return "OK"

                    if "reply_to_message" not in data["message"]:
                        M.sendmessage("需要reply訊息")
                        return "OK"
                    from_user_id = (data["message"]["reply_to_message"]
                                        ["from"]["id"])

                    if from_user_id == m_user_id:
                        M.sendmessage("你不能將自己除權")
                        return "OK"

                    count = M.cur.execute(
                        """DELETE FROM `admin` WHERE `user_id` = %s""",
                        (str(from_user_id))
                    )
                    M.db.commit()
                    if count == 0:
                        M.sendmessage("該用戶不是管理員")
                    else:
                        M.sendmessage(
                            "移除" +
                            (from_firstname + " " + from_lastname).strip() +
                            "(" + str(from_user_id) + ")為管理員"
                        )
                    return "OK"

                m = re.match(
                    r"/(?:adduser|au)(?:@cvn_smart_bot)?\s+(.+)(?:\n(.+))?",
                    m_text
                )
                if m is not None:
                    name = checkadmin()
                    if name is None:
                        return "OK"

                    user, wiki = M.parse_user(m.group(1))
                    reason = name + "加入：" + M.parse_reason(m.group(2))
                    M.addblack_user(user, m_date, reason, wiki)
                    M.adduser_score(M.user_type(user), 10, "handler/cmd/adduser")
                    return "OK"

                m = re.match(
                    r"/(?:userscore)(?:@cvn_smart_bot)?\s+(.+)(?:\n(.+))?",
                    m_text
                )
                if m is not None:
                    name = checkadmin()
                    if name is None:
                        return "OK"

                    user, wiki = M.parse_user(m.group(1))
                    point = 10
                    if m.group(2) is not None:
                        point = int(m.group(2))
                    userobj = M.user_type(user)
                    M.adduser_score(userobj, point, "handler/cmd/userscore")
                    M.sendmessage("userscore {} {}".format(userobj.val, point))
                    return "OK"

                m = re.match(
                    r"/addwhiteuser(?:@cvn_smart_bot)?\s+(.+)(?:\n(.+))?",
                    m_text
                )
                if m is not None:
                    name = checkadmin()
                    if name is None:
                        return "OK"

                    user = m.group(1)
                    reason = name+"加入："+M.parse_reason(m.group(2))
                    M.addwhite_user(user, m_date, reason)
                    return "OK"

                m = re.match(
                    r"/delwhiteuser(?:@cvn_smart_bot)?\s+(.+)(?:\n.+)?",
                    m_text
                )
                if m is not None:
                    if not checkadmin():
                        return "OK"

                    user = m.group(1)
                    M.delwhite_user(user)
                    return "OK"

                m = re.match(r"/(?:deluser|du)", m_text)
                if m is not None:
                    if not checkadmin():
                        return "OK"

                    m = re.match(
                        r"/(?:deluser|du)(?:@cvn_smart_bot)?\s+(.+)(?:\n.+)?",
                        m_text
                    )
                    if m is not None:
                        user, wiki = M.parse_user(m.group(1))
                    elif "reply_to_message" in data["message"]:
                        user = M.get_user_from_message_id(
                            data["message"]["reply_to_message"]["message_id"])
                        if len(user) == 0:
                            M.sendmessage("無法從訊息找到所對應的對象")
                            return "OK"
                        else:
                            user, wiki = M.parse_user(user[0][0])
                    else:
                        return "OK"

                    M.delblack_user(user, wiki)
                    return "OK"

                m = re.match(r"/setwiki", m_text)
                if m is not None:
                    if not checkadmin():
                        return "OK"

                    m = re.match(r"/(?:setwiki)(?:@cvn_smart_bot)?\s+(.+)?",
                                 m_text)
                    if "reply_to_message" in data["message"]:
                        user = M.get_user_from_message_id(
                            data["message"]["reply_to_message"]["message_id"])
                        if len(user) == 0:
                            M.sendmessage("無法從訊息找到所對應的對象")
                            return "OK"
                        else:
                            user, wiki = M.parse_user(user[0][0])
                        wiki = m.group(1).strip()
                    elif m is not None:
                        user, wiki = M.parse_user(m.group(1))
                    M.setwikiblack_user(user, wiki)

                    return "OK"

                m = re.match(
                    r"/(?:addpage|ap)(?:@cvn_smart_bot)?\s+(.+)(?:\n(.+))?",
                    m_text
                )
                if m is not None:
                    name = checkadmin()
                    if name is None:
                        return "OK"

                    page, wiki = M.parse_page(m.group(1))
                    reason = name+"加入："+M.parse_reason(m.group(2))
                    M.addblack_page(page, m_date, reason, wiki)
                    return "OK"

                m = re.match(
                    r"/massaddpage(?:@cvn_smart_bot)?\s+(.+(?:\n.+)*)\n(.+)",
                    m_text
                )
                if m is not None:
                    name = checkadmin()
                    if name is None:
                        return "OK"

                    for pageline in m.group(1).split("\n"):
                        page, wiki = M.parse_page(pageline)
                        reason = name+"加入："+M.parse_reason(m.group(2))
                        M.addblack_page(page, m_date, reason, wiki)
                    return "OK"

                m = re.match(r"/(?:delpage|dp)", m_text)
                if m is not None:
                    if not checkadmin():
                        return "OK"

                    m = re.match(
                        r"/(?:delpage|dp)(?:@cvn_smart_bot)?\s+(.+)(?:\n.+)?",
                        m_text
                    )
                    if m is not None:
                        page, wiki = M.parse_page(m.group(1))
                    elif "reply_to_message" in data["message"]:
                        page = M.get_page_from_message_id(
                            data["message"]["reply_to_message"]["message_id"])
                        if len(page) == 0:
                            M.sendmessage("無法從訊息找到所對應的頁面")
                            return "OK"
                        else:
                            page, wiki = M.parse_page(page[0][0])
                    else:
                        return "OK"

                    M.delblack_page(page, wiki)
                    return "OK"

                m = re.match(r"/(?:checkuser|cu)", m_text)
                if m is not None:
                    m = re.match(
                        r"/(?:checkuser|cu)(?:@cvn_smart_bot)?\s+(.+)",
                        m_text
                    )
                    if m is not None:
                        user, wiki = M.parse_user(m.group(1))
                    elif "reply_to_message" in data["message"]:
                        user = M.get_user_from_message_id(
                            data["message"]["reply_to_message"]["message_id"])
                        if len(user) == 0:
                            M.sendmessage("無法從訊息找到所對應的對象")
                            return "OK"
                        else:
                            user, wiki = M.parse_user(user[0][0])
                    else:
                        return "OK"

                    message = M.checkuser(user, wiki)
                    M.sendmessage(message)
                    return "OK"

                m = re.match(r"/(?:checkpage|cp)", m_text)
                if m is not None:
                    m = re.match(
                        r"/(?:checkpage|cp)(?:@cvn_smart_bot)?\s+(.+)",
                        m_text
                    )
                    if m is not None:
                        page, wiki = M.parse_page(m.group(1))
                    elif "reply_to_message" in data["message"]:
                        page = M.get_page_from_message_id(
                            data["message"]["reply_to_message"]["message_id"])
                        if len(page) == 0:
                            M.sendmessage("無法從訊息找到所對應的頁面")
                            return "OK"
                        else:
                            page, wiki = M.parse_page(page[0][0])
                    else:
                        return "OK"

                    message = ""
                    rows = M.check_page_blacklist(page, wiki)
                    if len(rows) != 0:
                        message += "\n於黑名單："
                        for record in rows:
                            message += ("\n" + M.parse_wikicode(record[0]) +
                                        ', ' + M.formattimediff(record[1]))

                    if message != "":
                        M.sendmessage(page+"@"+wiki+message)
                    else:
                        M.sendmessage(page+"@"+wiki+"：查無結果")
                    return "OK"

                if (re.match(r"/os(?:@cvn_smart_bot)?$", m_text)
                        and "reply_to_message" in data["message"]):
                    if not checkadmin():
                        return "OK"

                    M.deletemessage(data["message"]["message_id"])
                    M.deletemessage(data["message"]["reply_to_message"]
                                        ["message_id"])
                    return "OK"

                if (re.match(r"/osall(?:@cvn_smart_bot)?$", m_text)
                        and "reply_to_message" in data["message"]):
                    if not checkadmin():
                        return "OK"

                    M.deletemessage(data["message"]["message_id"])

                    message_id = (data["message"]["reply_to_message"]
                                      ["message_id"])
                    M.cur.execute("""SELECT `user` FROM `bot_message`
                                     WHERE `message_id` = %s""", (message_id))
                    rows = M.cur.fetchall()
                    if len(rows) == 0:
                        M.sendmessage("無法從訊息找到所對應的對象")
                        return "OK"
                    user = rows[0][0]

                    M.cur.execute("""SELECT `message_id` FROM `bot_message`
                                     WHERE `user` = %s""", (user))
                    rows = M.cur.fetchall()
                    for row in rows:
                        M.deletemessage(row[0])

                    M.sendmessage("已濫權掉"+str(len(rows))+"條訊息")
                    return "OK"

                m = re.match(r"/status", m_text)
                if m is not None:
                    message = (
                        ('Webhook: <a href="{}">WORKING!!</a>\n' +
                         '<a href="{}status">查看資料接收狀況</a>')
                        .format(
                            'https://zh.wikipedia.org/wiki/WORKING!!',
                            M.siteurl
                        )
                    )
                    M.sendmessage(message)
                    return "OK"

        return "OK"

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc())
        return "OK"


@app.route("/api", methods=['POST'])
def api():
    try:
        data = request.form.to_dict()

        if "token" not in data:
            return json.dumps({"message": "沒有給予存取權杖"})

        m = re.search(r"cvn_smart\(([a-z0-9]{32})\)", data["token"])
        if m is not None:
            data["token"] = m.group(1)

        def checkadmin():
            M.cur.execute(
                """SELECT `name` FROM `admin` WHERE `token` = %s""",
                (data["token"])
            )
            rows = M.cur.fetchall()
            if len(rows) == 0:
                return None
            return rows[0][0]

        if "action" not in data:
            return json.dumps({"message": "沒有給予操作類型"})

        if data["action"] == "authorize":
            name = checkadmin()
            if name is None:
                return json.dumps({"result": "fail"})
            return json.dumps({"result": "success", "user": name})

        if data["action"] == "addpage":
            name = checkadmin()
            if name is None:
                return json.dumps({"message": "你沒有權限", "nopermission": True})

            page, wiki = M.parse_page(data["page"])
            reason = name+"加入："+M.parse_reason(data["reason"])
            message = M.addblack_page(
                page,
                int(time.time()),
                reason,
                wiki,
                msgprefix=name+"透過API")
            return json.dumps({"message": message})

        if data["action"] == "delpage":
            name = checkadmin()
            if name is None:
                return json.dumps({"message": "你沒有權限", "nopermission": True})

            page, wiki = M.parse_page(data["page"])
            message = M.delblack_page(page, wiki, msgprefix=name+"透過API將")
            return json.dumps({"message": message})

        if data["action"] == "adduser":
            name = checkadmin()
            if name is None:
                return json.dumps({"message": "你沒有權限", "nopermission": True})

            user, wiki = M.parse_user(data["user"])
            reason = name+"加入："+M.parse_reason(data["reason"])
            message = M.addblack_user(
                user,
                int(time.time()),
                reason,
                wiki,
                msgprefix=name+"透過API")
            M.adduser_score(M.user_type(user), 10, "handler/api/adduser")
            return json.dumps({"message": message})

        if data["action"] == "deluser":
            name = checkadmin()
            if name is None:
                return json.dumps({"message": "你沒有權限", "nopermission": True})

            user, wiki = M.parse_user(data["user"])
            message = M.delblack_user(user, wiki, msgprefix=name+"透過API將")
            return json.dumps({"message": message})

        if data["action"] == "userscore":
            name = checkadmin()
            if name is None:
                return json.dumps({"message": "你沒有權限", "nopermission": True})

            user, wiki = M.parse_user(data["user"])
            point = int(data["point"])
            userobj = M.user_type(user)
            M.adduser_score(userobj, point, "handler/api/userscore")
            point2 = M.getuser_score(userobj)
            message = "為 {0} 調整分數 {1:+d} 為 {2}".format(user, point, point2)
            return json.dumps({"message": message})

        data["token"] = ""
        M.log(json.dumps(data, ensure_ascii=False))
        return json.dumps({"message": "伺服器沒有進行任何動作"})

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc())
        return json.dumps({"message": traceback.format_exc()})


@app.route("/gadget.js", methods=['GET'])
def gadget():
    filename = os.path.dirname(os.path.realpath(__file__))+"/gadget.js"
    return send_file(filename)


if __name__ == "__main__":
    app.run()
