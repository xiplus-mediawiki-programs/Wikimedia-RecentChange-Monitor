import re

from flask import make_response, render_template, request

from Monitor import Monitor


def web():
    M = Monitor()
    islogin = False
    loginname = ""
    if not islogin:
        logintoken = request.cookies.get("cvn_smart_token")
        if logintoken is not None:
            M.cur.execute(
                """SELECT `name` FROM `admin` WHERE `token` = %s""",
                (logintoken)
            )
            rows = M.cur.fetchall()
            if len(rows) != 0:
                islogin = True
                loginname = rows[0][0]

    setcookie = {}
    html = ""
    if "type" in request.args:
        if request.args["type"] == "login":
            if "logintoken" in request.form:
                logintoken = request.form["logintoken"]
                m = re.search(r"cvn_smart\(([a-z0-9]{32})\)", logintoken)
                if m is not None:
                    logintoken = m.group(1)
                M.cur.execute(
                    """SELECT `name` FROM `admin` WHERE `token` = %s""",
                    (logintoken)
                )
                rows = M.cur.fetchall()
                if len(rows) == 0:
                    html = "登入失敗"
                else:
                    islogin = True
                    loginname = rows[0][0]
                    html = "登入成功"
                    setcookie["cvn_smart_token"] = logintoken
            else:
                html = "您沒有提供存取權杖"
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
                """SELECT `wiki`, `user`, `point`, `reason`, `black_user`.`timestamp`
                   FROM `black_user`
                   LEFT JOIN `user_score`
                   ON `black_user`.`userhash` = `user_score`.`userhash`
                   WHERE `point` <= 0
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
        elif request.args["type"] == "blackpage":
            if "delpage" in request.form:
                if islogin:
                    page, wiki = M.parse_page(request.form["delpage"])
                    M.delblack_page(page, wiki, msgprefix=loginname + "透過網頁將")
                    html += "成功取消監視 {}({})".format(page, wiki)
                else:
                    html += "你沒有權限取消監視頁面"

            M.cur.execute("""SELECT `wiki`, `page`, `point`, `reason`, `timestamp`
                             FROM `black_page` ORDER BY `timestamp` DESC""")
            rows = M.cur.fetchall()
            html += """
                <form action="?type=blackpage" method="POST">
                <table>
                <tr>
                    <th>wiki</th>
                    <th>page</th>
                """
            if islogin:
                html += "<th>unwatch</th>"
            html += """
                    <th>point</th>
                    <th>reason</th>
                    <th>timestamp</th>
                </tr>
                """
            for row in rows:
                temp = """
                    <tr>
                        <td>{0}</td>
                        <td>{1}</td>
                    """
                if islogin:
                    temp += """<td><button type="submit" name="delpage" value="{1}|{0}">unwatch</button></td>"""
                temp += """
                        <td>{2}</td>
                        <td>{3}</td>
                        <td>{4}</td>
                    </tr>
                    """
                html += temp.format(
                    row[0],
                    row[1],
                    row[2],
                    M.parse_wikicode(row[3]),
                    M.formattimediff(row[4])
                )
            html += """
                </table>
                </form>
                """
    response = make_response(render_template('blacklist.html', maincontent=html, hidelogin=islogin, loginname=loginname))
    for key in setcookie:
        response.set_cookie(key, setcookie[key], path="/wikipedia_rc")
    return response
