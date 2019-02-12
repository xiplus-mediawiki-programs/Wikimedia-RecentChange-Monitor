import json
import re
import time
import traceback
import urllib

from flask import request

from Monitor import Monitor


def web():
    M = Monitor()
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

        if data["action"] == "centralauthorize":
            query = {
                "format": "json",
                "action": "query",
                "meta": "userinfo",
                "centralauthtoken": data["centralauthtoken"]
            }
            query = urllib.parse.urlencode(query)
            url = "https://meta.wikimedia.org/w/api.php?" + query
            res = urllib.request.urlopen(url).read().decode("utf8")
            res = json.loads(res)

            if "query" in res:
                wiki_username = res["query"]["userinfo"]["name"]
                M.cur.execute(
                    """SELECT `name`, `token` FROM `admin` WHERE `wiki_username` = %s""",
                    (wiki_username)
                )
                rows = M.cur.fetchall()
                if len(rows) == 0:
                    return json.dumps({"result": "fail"})
                return json.dumps({"result": "success", "user": rows[0][0], "token": rows[0][1]})

            return json.dumps({"result": "fail"})

        if data["action"] == "updatecentralinfo":
            name = checkadmin()
            if name is None:
                return json.dumps({"result": "fail"})

            query = {
                "format": "json",
                "action": "query",
                "meta": "userinfo",
                "centralauthtoken": data["centralauthtoken"]
            }
            query = urllib.parse.urlencode(query)
            url = "https://meta.wikimedia.org/w/api.php?" + query
            res = urllib.request.urlopen(url).read().decode("utf8")
            res = json.loads(res)

            if "query" in res:
                wiki_username = res["query"]["userinfo"]["name"]
                count = M.cur.execute(
                    """UPDATE `admin` SET `wiki_username` = %s
                   WHERE `token` = %s""",
                    (wiki_username, data["token"]))
                M.db.commit()
                if count == 0:
                    return json.dumps({"result": "fail"})
                return json.dumps({"result": "success", "wiki_username": wiki_username, "user": name})

            return json.dumps({"result": "fail"})

        if data["action"] == "addpage":
            name = checkadmin()
            if name is None:
                return json.dumps({"message": "你沒有權限", "nopermission": True})

            page, wiki = M.parse_page(data["page"])
            try:
                point = int(data["point"])
            except ValueError:
                point = 30

            reason = name + "加入：" + M.parse_reason(data["reason"])
            message = M.addblack_page(
                page,
                int(time.time()),
                reason,
                point,
                wiki,
                msgprefix=name + "透過API")
            return json.dumps({"message": message})

        if data["action"] == "delpage":
            name = checkadmin()
            if name is None:
                return json.dumps({"message": "你沒有權限", "nopermission": True})

            page, wiki = M.parse_page(data["page"])
            message = M.delblack_page(page, wiki, msgprefix=name + "透過API將")
            return json.dumps({"message": message})

        if data["action"] == "pagescore":
            name = checkadmin()
            if name is None:
                return json.dumps({"message": "你沒有權限", "nopermission": True})

            page, wiki = M.parse_user(data["page"])
            try:
                point = int(data["point"])
            except ValueError:
                point = 30

            M.addpage_score(page, wiki, point)
            point2 = M.getpage_score(page, wiki)
            message = "為 {0} 調整分數 {1:+d} 為 {2}".format(page, point, point2)
            return json.dumps({"message": message})

        if data["action"] == "adduser":
            name = checkadmin()
            if name is None:
                return json.dumps({"message": "你沒有權限", "nopermission": True})

            user, wiki = M.parse_user(data["user"])
            reason = name + "加入：" + M.parse_reason(data["reason"])
            message = M.addblack_user(
                user,
                int(time.time()),
                reason,
                wiki,
                msgprefix=name + "透過API")
            try:
                point = int(data["point"])
            except ValueError:
                point = 10
            M.adduser_score(M.user_type(user), point, "handler/api/adduser")
            return json.dumps({"message": message})

        if data["action"] == "deluser":
            name = checkadmin()
            if name is None:
                return json.dumps({"message": "你沒有權限", "nopermission": True})

            user, wiki = M.parse_user(data["user"])
            message = M.delblack_user(user, wiki, msgprefix=name + "透過API將")
            return json.dumps({"message": message})

        if data["action"] == "userscore":
            name = checkadmin()
            if name is None:
                return json.dumps({"message": "你沒有權限", "nopermission": True})

            user, wiki = M.parse_user(data["user"])
            try:
                point = int(data["point"])
            except ValueError:
                point = 10
            userobj = M.user_type(user)
            M.adduser_score(userobj, point, "handler/api/userscore")
            point2 = M.getuser_score(userobj)
            message = "為 {0} 調整分數 {1:+d} 為 {2}".format(user, point, point2)
            return json.dumps({"message": message})

        data["token"] = ""
        M.log(json.dumps(data, ensure_ascii=False))
        return json.dumps({"message": "伺服器沒有進行任何動作"})

    except Exception:
        traceback.print_exc()
        M.error(traceback.format_exc())
        return json.dumps({"message": traceback.format_exc()})
