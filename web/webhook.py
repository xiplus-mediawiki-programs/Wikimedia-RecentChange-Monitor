import json
import re
import traceback

from flask import request

from Monitor import Monitor


def web():
    M = Monitor()
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
                    point2 = M.getuser_score(userobj)
                    message = "為 {0} 調整分數 {1:+d} 為 {2}".format(user, point, point2)
                    M.sendmessage(message)
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
                    reason = name + "加入：" + M.parse_reason(m.group(2))
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
                    reason = name + "加入：" + M.parse_reason(m.group(2))
                    M.addblack_page(page, m_date, reason, wiki=wiki)
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
                        reason = name + "加入：" + M.parse_reason(m.group(2))
                        M.addblack_page(page, m_date, reason, wiki=wiki)
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
                        M.sendmessage(page + "@" + wiki + message)
                    else:
                        M.sendmessage(page + "@" + wiki + "：查無結果")
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

                    M.sendmessage("已濫權掉" + str(len(rows)) + "條訊息")
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

    except Exception:
        traceback.print_exc()
        M.error(traceback.format_exc())
        return "OK"
