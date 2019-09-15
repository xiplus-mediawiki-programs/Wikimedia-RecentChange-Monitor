import argparse
import contextlib
import io
import json
import re
import shlex
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
                M.log(m_text, logtype='webhook')

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

                def handle_parser(parser, cmd):
                    with io.StringIO() as buf, contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                        try:
                            args = parser.parse_args(cmd)
                        except SystemExit:
                            output = buf.getvalue()
                            M.sendmessage(output)
                            return None
                        except Exception:
                            M.error(traceback.format_exc())
                            return None
                        else:
                            return args

                cmd = shlex.split(m_text)
                action = cmd[0]
                cmd = cmd[1:]
                action = action[1:]
                action = re.sub(r'@cvn_smart_bot$', '', action)
                action = action.lower()

                if action in ['gettoken'] and m_chat_id == m_user_id:
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

                if action in ['newtoken'] and m_chat_id == m_user_id:
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

                if action in ['setadmin']:
                    if not checkadmin():
                        return "OK"

                    parser = argparse.ArgumentParser(
                        prog='/{0}'.format(action))
                    parser.add_argument(
                        'nickname', type=str, default=None, nargs='?', help='用戶暱稱')

                    args = handle_parser(parser, cmd)
                    if args is None:
                        return 'OK'

                    if "reply_to_message" not in data["message"]:
                        M.sendmessage("需要reply訊息")
                        return "OK"

                    name = from_firstname
                    if args.nickname is not None and args.nickname.strip() != '':
                        name = args.nickname

                    M.cur.execute("""REPLACE INTO `admin` (`user_id`, `name`)
                                     VALUES (%s, %s)""",
                                  (str(from_user_id), name))
                    M.db.commit()
                    M.sendmessage(
                        "設定" + name + "("
                        + (from_firstname + " " + from_lastname).strip()
                        + ")(" + str(from_user_id) + ")為管理員"
                    )
                    return "OK"

                if action in ['deladmin']:
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
                            "移除"
                            + (from_firstname + " " + from_lastname).strip()
                            + "(" + str(from_user_id) + ")為管理員"
                        )
                    return "OK"

                if action in ['adduser', 'au']:
                    name = checkadmin()
                    if name is None:
                        return "OK"

                    parser = argparse.ArgumentParser(
                        prog='/{0}'.format(action))
                    parser.add_argument('username', type=str, default=None, nargs='?', help='用戶名')
                    parser.add_argument('reason', type=str,
                                        default='無原因', nargs='?', help='原因')
                    parser.add_argument('-w', '--wiki', type=str, metavar='站點',
                                        help='參見 https://quarry.wmflabs.org/query/278 ，預設：zhwiki')
                    parser.add_argument(
                        '-r', '--reason', type=str, metavar='原因', default='無原因', help='預設：%(default)s')
                    parser.add_argument(
                        '-p', '--point', type=int, metavar='點數', default=10, help='預設：%(default)s')

                    args = handle_parser(parser, cmd)
                    if args is None:
                        return 'OK'

                    user = args.username
                    if user is None and 'reply_to_message' in data['message']:
                        user = M.get_user_from_message_id(
                            data["message"]["reply_to_message"]["message_id"])
                        if len(user) == 0:
                            M.sendmessage("無法從訊息找到所對應的對象")
                            return "OK"
                        user = user[0][0]

                    if user is None:
                        M.sendmessage('未指定用戶名')
                        return "OK"

                    user, wiki = M.parse_user(user)

                    if args.wiki is not None:
                        wiki = args.wiki

                    reason = name + '加入：' + args.reason
                    M.addblack_user(user, m_date, reason, wiki)
                    M.adduser_score(M.user_type(user), args.point)
                    return 'OK'

                if action in ['userscore', 'us']:
                    name = checkadmin()
                    if name is None:
                        return "OK"

                    parser = argparse.ArgumentParser(prog='/{0}'.format(action))
                    if 'reply_to_message' in data['message']:
                        user = M.get_user_from_message_id(
                            data["message"]["reply_to_message"]["message_id"])
                        if len(user) == 0:
                            M.sendmessage("無法從訊息找到所對應的對象")
                            return "OK"
                        user = user[0][0]
                        parser.add_argument('point', type=int, nargs='?', default=10, help='點數，預設：%(default)s')
                    else:
                        parser.add_argument('username', type=str, help='用戶名')
                        parser.add_argument('point', type=int, nargs='?', default=10, help='點數，預設：%(default)s')

                    args = handle_parser(parser, cmd)
                    if args is None:
                        return 'OK'

                    if 'reply_to_message' not in data['message']:
                        user = args.username

                    user, wiki = M.parse_user(user)
                    point = args.point
                    userobj = M.user_type(user)
                    M.adduser_score(userobj, point)
                    point2 = M.getuser_score(userobj)
                    message = "為 {0} 調整分數 {1:+d} 為 {2}".format(
                        user, point, point2)
                    M.sendmessage(message)
                    return "OK"

                if action in ['deluser', 'du']:
                    if not checkadmin():
                        return "OK"

                    parser = argparse.ArgumentParser(
                        prog='/{0}'.format(action))
                    parser.add_argument(
                        'username', type=str, default=None, nargs='?', help='用戶名')
                    parser.add_argument(
                        'reason', type=str, default=None, nargs='?', help='原因')  # Unused
                    parser.add_argument('-w', '--wiki', type=str, metavar='站點',
                                        help='參見 https://quarry.wmflabs.org/query/278 ，預設：zhwiki')

                    args = handle_parser(parser, cmd)
                    if args is None:
                        return 'OK'

                    user = args.username
                    if user is None and 'reply_to_message' in data['message']:
                        user = M.get_user_from_message_id(
                            data["message"]["reply_to_message"]["message_id"])
                        if len(user) == 0:
                            M.sendmessage("無法從訊息找到所對應的對象")
                            return "OK"
                        user = user[0][0]

                    if user is None:
                        M.sendmessage('未指定用戶名')
                        return "OK"

                    user, wiki = M.parse_user(user)

                    if args.wiki is not None:
                        wiki = args.wiki

                    M.delblack_user(user, wiki)
                    return "OK"

                if action in ['setwiki']:
                    if not checkadmin():
                        return "OK"

                    parser = argparse.ArgumentParser(
                        prog='/{0}'.format(action))
                    parser.add_argument('wiki', type=str, default='zhwiki', metavar='站點',
                                        help='參見 https://quarry.wmflabs.org/query/278 ，預設：zhwiki')
                    parser.add_argument(
                        '-u', '--user', dest='username', type=str, metavar='用戶名')

                    args = handle_parser(parser, cmd)
                    if args is None:
                        return 'OK'

                    user = args.username
                    if user is None and 'reply_to_message' in data['message']:
                        user = M.get_user_from_message_id(
                            data["message"]["reply_to_message"]["message_id"])
                        if len(user) == 0:
                            M.sendmessage("無法從訊息找到所對應的對象")
                            return "OK"
                        user = user[0][0]

                    if user is None:
                        return 'OK'

                    user, _ = M.parse_user(user)

                    M.setwikiblack_user(user, args.wiki)
                    return "OK"

                if action in ['addpage', 'ap']:
                    name = checkadmin()
                    if name is None:
                        return "OK"

                    parser = argparse.ArgumentParser(
                        prog='/{0}'.format(action))
                    parser.add_argument('pagetitle', type=str, default=None, nargs='?', help='頁面名')
                    parser.add_argument('reason', type=str,
                                        default='無原因', nargs='?', help='原因')
                    parser.add_argument('-w', '--wiki', type=str, metavar='站點',
                                        help='參見 https://quarry.wmflabs.org/query/278 ，預設：zhwiki')
                    parser.add_argument(
                        '-r', '--reason', type=str, metavar='原因', default='無原因', help='預設：%(default)s')
                    parser.add_argument(
                        '-p', '--point', type=int, metavar='點數', default=30, help='預設：%(default)s')

                    args = handle_parser(parser, cmd)
                    if args is None:
                        return 'OK'

                    page = args.pagetitle
                    if page is None and 'reply_to_message' in data['message']:
                        page = M.get_page_from_message_id(
                            data["message"]["reply_to_message"]["message_id"])
                        if len(page) == 0:
                            M.sendmessage("無法從訊息找到所對應的頁面")
                            return "OK"
                        page = page[0][0]

                    if page is None:
                        M.sendmessage('未指定頁面標題')
                        return 'OK'

                    page, wiki = M.parse_page(page)

                    if args.wiki is not None:
                        wiki = args.wiki

                    reason = name + '加入：' + M.parse_reason(args.reason)
                    M.addblack_page(page, m_date, reason,
                                    wiki=wiki, point=args.point)
                    return "OK"

                if action in ['massaddpage']:
                    name = checkadmin()
                    if name is None:
                        return "OK"

                    parser = argparse.ArgumentParser(
                        prog='/{0}'.format(action))
                    parser.add_argument(
                        'pagetitle', type=str, nargs='+', help='頁面名')
                    parser.add_argument('-w', '--wiki', type=str, metavar='站點',
                                        help='參見 https://quarry.wmflabs.org/query/278 ，預設：zhwiki')
                    parser.add_argument(
                        '-r', '--reason', type=str, metavar='原因', default='無原因', help='預設：%(default)s')
                    parser.add_argument(
                        '-p', '--point', type=int, metavar='點數', default=30, help='預設：%(default)s')

                    args = handle_parser(parser, cmd)
                    if args is None:
                        return 'OK'

                    for page in args.pagetitle:
                        page, wiki = M.parse_page(page)

                        if args.wiki is not None:
                            wiki = args.wiki

                        reason = name + '加入：' + M.parse_reason(args.reason)
                        M.addblack_page(page, m_date, reason,
                                        wiki=wiki, point=args.point)
                    return "OK"

                if action in ['delpage', 'dp']:
                    if not checkadmin():
                        return "OK"

                    parser = argparse.ArgumentParser(
                        prog='/{0}'.format(action))
                    parser.add_argument(
                        'pagetitle', type=str, default=None, nargs='?', help='頁面名')
                    parser.add_argument(
                        'reason', type=str, default=None, nargs='?', help='原因')  # Unused
                    parser.add_argument('-w', '--wiki', type=str, metavar='站點',
                                        help='參見 https://quarry.wmflabs.org/query/278 ，預設：zhwiki')

                    args = handle_parser(parser, cmd)
                    if args is None:
                        return 'OK'

                    page = args.pagetitle
                    if page is None and 'reply_to_message' in data['message']:
                        page = M.get_page_from_message_id(
                            data["message"]["reply_to_message"]["message_id"])
                        if len(page) == 0:
                            M.sendmessage("無法從訊息找到所對應的頁面")
                            return "OK"
                        page = page[0][0]

                    if page is None:
                        M.sendmessage('未指定頁面標題')
                        return 'OK'

                    page, wiki = M.parse_page(page)

                    if args.wiki is not None:
                        wiki = args.wiki

                    M.delblack_page(page, wiki)
                    return "OK"

                if action in ['checkuser', 'cu']:
                    parser = argparse.ArgumentParser(
                        prog='/{0}'.format(action))
                    parser.add_argument(
                        'username', type=str, default=None, nargs='?', help='用戶名')
                    parser.add_argument('-w', '--wiki', type=str, metavar='站點',
                                        help='參見 https://quarry.wmflabs.org/query/278 ，預設：zhwiki')

                    args = handle_parser(parser, cmd)
                    if args is None:
                        return 'OK'

                    user = args.username
                    if user is None and 'reply_to_message' in data['message']:
                        user = M.get_user_from_message_id(
                            data["message"]["reply_to_message"]["message_id"])
                        if len(user) == 0:
                            M.sendmessage("無法從訊息找到所對應的對象")
                            return "OK"
                        user = user[0][0]

                    if user is None:
                        M.sendmessage('未指定用戶名')
                        return "OK"

                    user, wiki = M.parse_user(user)

                    if args.wiki is not None:
                        wiki = args.wiki

                    message = M.checkuser(user, wiki)
                    M.sendmessage(message)
                    return "OK"

                if action in ['checkpage', 'cp']:
                    parser = argparse.ArgumentParser(
                        prog='/{0}'.format(action))
                    parser.add_argument(
                        'pagetitle', type=str, default=None, nargs='?', help='頁面名')
                    parser.add_argument('-w', '--wiki', type=str, metavar='站點',
                                        help='參見 https://quarry.wmflabs.org/query/278 ，預設：zhwiki')

                    args = handle_parser(parser, cmd)
                    if args is None:
                        return 'OK'

                    page = args.pagetitle
                    if page is None and 'reply_to_message' in data['message']:
                        page = M.get_page_from_message_id(
                            data["message"]["reply_to_message"]["message_id"])
                        if len(page) == 0:
                            M.sendmessage("無法從訊息找到所對應的頁面")
                            return "OK"
                        page = page[0][0]

                    if page is None:
                        M.sendmessage('未指定頁面標題')
                        return 'OK'

                    page, wiki = M.parse_page(page)

                    if args.wiki is not None:
                        wiki = args.wiki

                    message = ""
                    rows = M.check_page_blacklist(page, wiki)
                    if len(rows) != 0:
                        message += "\n於黑名單："
                        for record in rows:
                            message += ("\n" + M.parse_wikicode(record[0])
                                        + ', ' + M.formattimediff(record[1]))

                    if message != "":
                        M.sendmessage(page + "@" + wiki + message)
                    else:
                        M.sendmessage(page + "@" + wiki + "：查無結果")
                    return "OK"

                if action in ['os'] and 'reply_to_message' in data['message']:
                    if not checkadmin():
                        return "OK"

                    M.deletemessage(data["message"]["message_id"])
                    M.deletemessage(data["message"]["reply_to_message"]
                                        ["message_id"])
                    return "OK"

                if action in ['osall'] and 'reply_to_message' in data['message']:
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

                    return "OK"

                if action in ['status']:
                    message = (
                        ('Webhook: <a href="{}">WORKING!!</a>\n'
                         + '<a href="{}status">查看資料接收狀況</a>')
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
